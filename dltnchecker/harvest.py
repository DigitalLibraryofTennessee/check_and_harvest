import requests
from lxml import etree
import json
import xmltodict
import os


class OAIChecker:
    """A class to run tests and harvest of metadata records via OAI-PMH.

    Attributes:
        oai_base_url (str): The base url of the OAI-PMH endpoint.
        harvest (bool): Whether or not good records will be serialized to disk.
        endpoint (str): Full OAI-PMH request.
        metadata_prefix (str): The metadata prefix to use in OAI-PMH requests.
        metadata_key (str): The key of the root metadata record.
        set (str): The set to be harvested via OAI-PMH or an empty string.
        bad_records (int): The total number of bad objects found in this request.
    """
    def __init__(self, endpoint, oai_set="", prefix="oai_dc", harvest=True):
        self.oai_base_url = endpoint
        self.harvest = harvest
        self.endpoint = self.set_endpoint(endpoint, oai_set, prefix)
        self.__token = ""
        self.metadata_prefix = prefix
        self.metadata_key = self.__set_metadata_key(prefix)
        self.__status = "In Progress"
        self.set = oai_set
        self.bad_records = 0

    @staticmethod
    def __set_metadata_key(metadata_format):
        metadata_keys = {
            'oai_dc': 'oai_dc:dc',
            'oai_qdc': 'oai_qdc:qualifieddc',
            'xoai': 'xoai',
            'mods': 'mods',
            'MODS': 'mods',
        }
        return metadata_keys[metadata_format]

    @staticmethod
    def set_endpoint(our_endpoint, our_set, our_prefix):
        endpoint = f"{our_endpoint}?verb=ListRecords&metadataPrefix={our_prefix}"
        if our_set != "":
            endpoint = f"{endpoint}&set={our_set}"
        return endpoint

    def __get_root_tag_and_namespace(self):
        root_tag = {
            'oai_dc': './/{http://www.openarchives.org/OAI/2.0/oai_dc/}dc',
            'oai_qdc': './/{http://worldcat.org/xmlschemas/qdc-1.0/}qualifieddc',
            'xoai': './/{http://www.lyncode.com/xoai}metadata',
            'mods': './/{http://www.loc.gov/mods/v3}mods',
            'MODS': './/{http://www.loc.gov/mods/v3}mods',
        }
        return root_tag[self.metadata_prefix]

    def process_token(self, token):
        if len(token) == 1:
            self.__token = f'&resumptionToken={token[0].text}'
        else:
            self.__status = "Done"
        return

    def list_records(self):
        r = requests.get(f"{self.endpoint}")
        oai_document = etree.fromstring(r.content)
        self.process_token(oai_document.findall('.//{http://www.openarchives.org/OAI/2.0/}resumptionToken'))
        self.__process_records(oai_document.findall('.//{http://www.openarchives.org/OAI/2.0/}record'))
        if self.__status is not "Done":
            self.endpoint = f"{self.oai_base_url}?verb=ListRecords{self.__token}"
            return self.list_records()
        else:
            return

    def __process_records(self, all_metadata):
        for record in all_metadata:
            filename = xmltodict.parse(etree.tostring(record))["record"]["header"]["identifier"]
            metadata = etree.fromstring(etree.tostring(record).decode("utf-8"))
            record = metadata.findall(self.__get_root_tag_and_namespace())
            if len(record) != 0:
                for rec in record:
                    record_as_xml = etree.tostring(rec)
                    record_as_json = json.loads(json.dumps(xmltodict.parse(record_as_xml)))
                    record_test = self.__record_test(record_as_json)
                    if record_test.is_good is True and self.harvest is True:
                        self.__write_to_disk(record_as_xml, filename)
                    elif record_test.is_good is False:
                        self.bad_records += 1
                        self.__write_bad_records_to_log(record_as_json)
        return

    def __record_test(self, some_json):
        if self.metadata_key == "oai_dc:dc":
            return DCTester(self.metadata_key, some_json)
        elif self.metadata_key == "xoai":
            return XOAITester(some_json)
        elif self.metadata_key == "mods":
            return MODSTester(some_json)

    @staticmethod
    def __write_to_disk(document, name):
        filename = name.split(":")[-1].replace("/", "_")
        if not os.path.exists("output"):
            os.makedirs("output")
        with open(f"output/{filename}.xml", "w") as xml_file:
            xml_file.write(document.decode("utf-8"))
        return

    @staticmethod
    def __write_bad_records_to_log(bad_record):
        with open("bad_records.log", 'a+') as bad_records:
            bad_records.write(f'This is a bad record:\n  {bad_record}\n')
        return


class DCTester:
    """A class to test DC records

        Attributes:
            metadata_key (str): The base node of the metadata rcord.
            document (dict):  The DC record to be tested.
            is_good (bool): Whether or not the document passed defined tests.
        """
    def __init__(self, metadata_format, document):
        self.metadata_key = metadata_format
        self.document = document
        self.is_good = self.__test()

    def __test(self):
        tests = [
            self.__check_for_title(),
            self.__check_for_rights(),
            self.__check_identifiers(),
        ]
        if False in tests:
            return False
        else:
            return True

    def __check_for_title(self):
        try:
            if self.document[self.metadata_key]["dc:title"]:
                return True
        except KeyError:
            return False

    def __check_for_rights(self):
        try:
            for k, v in self.document[self.metadata_key].items():
                if k == "dc:rights":
                    return True
                elif k == "dcterms:accessRights":
                    return True
            return False
        except KeyError:
            return False

    def __check_identifiers(self):
        identifiers = self.document[self.metadata_key]["dc:identifier"]
        try:
            if type(identifiers) is str:
                if identifiers.startswith("http"):
                    return True
                else:
                    return False
            elif type(identifiers) is list:
                good = False
                for identifier in identifiers:
                    if identifier.startswith("http"):
                        good = True
                return good
            else:
                return False
        except KeyError:
            return False


class XOAITester:
    """A class to run tests of xoai records.

    Attributes:
        document (dict): The metadata document to be tested as a dict.
        is_good (bool): Whether the tested document passed the defined tests.
    """
    def __init__(self, document):
        self.document = document
        self.is_good = self.__test()

    def __test(self):
        checks = [
            self.__check_thumbnails(),
            self.__check_titles(),
            self.__check_for_a_handle(),
        ]
        if False in checks:
            return False
        else:
            return True

    def __check_titles(self):
        has_a_title = False
        try:
            for k, v in self.document['metadata'].items():
                if type(v) is list:
                    for element in v:
                        if element['@name'] == 'dc':
                            for thing in element['element']:
                                if thing['@name'] == 'title':
                                    has_a_title = True
        except KeyError:
            pass
        except TypeError:
            pass
        return has_a_title

    def __check_for_a_handle(self):
        has_a_handle = False
        try:
            for k, v in self.document['metadata'].items():
                if type(v) is list:
                    for element in v:
                        if element['@name'] == 'dc':
                            for thing in element['element']:
                                if thing['@name'] == 'identifier':
                                    if thing['element']['@name'] == 'uri':
                                        has_a_handle = True
        except KeyError:
            pass
        except TypeError:
            pass
        return has_a_handle

    def __check_thumbnails(self):
        has_thumbnail = False
        try:
            for bundle in self.document['metadata']['element'][1]['element']:
                try:
                    if bundle['field']['#text'] == 'THUMBNAIL':
                        has_thumbnail = True
                except TypeError:
                    pass
        except KeyError:
            pass
        return has_thumbnail


class MODSTester:
    """A class to test MODS records

    Attributes:
        document (dict):  The MODS record to be tested.
        is_good (bool): Whether or not the document passed defined tests.
    """
    def __init__(self, document):
        self.document = document
        self.is_good = self.__test()

    def __test(self):
        checks = [
            self.__check_for_title(),
            self.__check_record_content_source(),
            self.__check_rights(),
            self.__check_thumbnails(),
            self.__check_object_in_context(),
        ]
        if False in checks:
            return False
        else:
            return True

    def __check_for_title(self):
        has_title = False
        try:
            title_info = self.document['mods']['titleInfo']
            if type(title_info) is list:
                for title in title_info:
                    if "@type" in title['title']:
                        if title['title']['@type'] != "alternative":
                            has_title = True
                    elif type(title['title']) is str:
                        has_title = True
            elif type(title_info) is dict:
                if "@type" in title_info['title']:
                    if title_info['title']['@type'] != "alternative":
                        has_title = True
                elif type(title_info['title']) is str:
                    has_title = True
                elif type(title_info['title']) is list:
                    for title in (title_info['title']):
                        if "@type" in title:
                            if title['@type'] != "alternative":
                                has_title = True
                        elif type(title) is str:
                            has_title = True
        except KeyError:
            pass
        return has_title

    def __check_record_content_source(self):
        has_record_content_source = False
        try:
            record_info = self.document['mods']['recordInfo']
            if 'recordContentSource' in record_info:
                has_record_content_source = True
        except KeyError:
            pass
        return has_record_content_source

    def __check_rights(self):
        has_rights = False
        try:
            if 'accessCondition' in self.document['mods']:
                access_condition = self.document['mods']['accessCondition']
                if '@type' in access_condition:
                    if access_condition['@type'] == 'use and reproduction' and '@xlink:href' in access_condition:
                        has_rights = True
                    elif access_condition['@type'] == 'local rights statement':
                        has_rights = True
                elif type(access_condition) is list:
                    for rights in access_condition:
                        if '@type' in rights:
                            if rights['@type'] == 'use and reproduction' and '@xlink:href' in rights:
                                has_rights = True
                            elif rights['@type'] == 'local rights statement':
                                has_rights = True
        except KeyError:
            pass
        return has_rights

    def __check_thumbnails(self):
        has_a_thumbnail = False
        location = self.document['mods']['location']
        try:
            if 'url' in location:
                for url in location['url']:
                    if url['@access'] == "preview":
                        has_a_thumbnail = True
        except KeyError:
            pass
        except TypeError:
            pass
        return has_a_thumbnail

    def __check_object_in_context(self):
        has_object_in_context = False
        location = self.document['mods']['location']
        try:
            if 'url' in location:
                for url in location['url']:
                    if url['@access'] == "object in context":
                        has_object_in_context = True
        except KeyError:
            pass
        except TypeError:
            pass
        return has_object_in_context


if __name__ == "__main__":
    # x = OAIRequest("http://nashville.contentdm.oclc.org/oai/oai.php", "nr", "oai_qdc").list_records()
    x = OAIChecker("http://dlynx.rhodes.edu:8080/oai/request", "col_10267_34285", "xoai")
    x.list_records()
    print(f'Set currently has {x.bad_records} bad records.')

import requests
from lxml import etree
import json
import xmltodict


class OAIRequest:
    def __init__(self, endpoint, oai_set="", prefix="oai_dc", harvest=True):
        self.oai_base = endpoint
        self.harvest = harvest
        self.endpoint = self.set_endpoint(endpoint, oai_set, prefix)
        self.token = ""
        self.metadata_prefix = prefix
        self.metadata_key = self.__set_metadata_key(prefix)
        self.status = "In Progress"
        self.set = oai_set
        self.bad_records = 0

    @staticmethod
    def __set_metadata_key(metadata_format):
        if metadata_format == "oai_dc":
            return "oai_dc:dc"
        elif metadata_format == "oai_qdc":
            return "oai_qdc:qualifieddc"
        elif metadata_format == "xoai":
            return "xoai"
        elif metadata_format == "MODS" or metadata_format == "mods":
            return "mods"

    @staticmethod
    def set_endpoint(our_endpoint, our_set, our_prefix):
        endpoint = f"{our_endpoint}?verb=ListRecords&metadataPrefix={our_prefix}"
        if our_set != "":
            endpoint = f"{endpoint}&set={our_set}"
        return endpoint

    def __get_root_tag_and_namespace(self):
        if self.metadata_prefix == "oai_dc":
            return './/{http://www.openarchives.org/OAI/2.0/oai_dc/}dc'
        elif self.metadata_prefix == "oai_qdc":
            return './/{http://worldcat.org/xmlschemas/qdc-1.0/}qualifieddc'
        elif self.metadata_prefix == "xoai":
            return './/{http://www.lyncode.com/xoai}metadata'
        elif self.metadata_prefix == 'mods' or self.metadata_prefix == 'MODS':
            return './/{http://www.loc.gov/mods/v3}mods'

    def process_token(self, token):
        if len(token) == 1:
            self.token = f'&resumptionToken={token[0].text}'
            return
        else:
            self.status = "Done"
            return

    def list_records(self):
        r = requests.get(f"{self.endpoint}")
        oai_document = etree.fromstring(r.content)
        self.process_token(oai_document.findall('.//{http://www.openarchives.org/OAI/2.0/}resumptionToken'))
        self.__process_records(oai_document.findall('.//{http://www.openarchives.org/OAI/2.0/}record'))
        if self.status is not "Done":
            self.endpoint = f"{self.oai_base}?verb=ListRecords{self.token}"
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
                    if self.metadata_key == "oai_dc:dc":
                        dc_record = DCTester(self.metadata_key, record_as_json)
                        if dc_record.is_good is True:
                            self.__write_to_disk(record_as_xml, filename)
                        else:
                            self.bad_records += 1
                            self.__write_bad_records_to_log(record_as_json)
                    elif self.metadata_key == "xoai":
                        xoai_record = XOAITester(record_as_json)
                        if xoai_record.is_good is True:
                            self.__write_to_disk(record_as_xml, filename)
                        else:
                            self.bad_records += 1
                            self.__write_bad_records_to_log(record_as_json)
                    elif self.metadata_key == "mods":
                        mods_record = MODSTester(record_as_json)
                        if mods_record.is_good is True:
                            self.__write_to_disk(record_as_xml, filename)
                        else:
                            self.bad_records += 1
                            self.__write_bad_records_to_log(record_as_json)
        return

    @staticmethod
    def __write_to_disk(document, name):
        filename = name.split(":")[-1].replace("/", "_")
        with open(f"output/{filename}.xml", "w") as xml_file:
            xml_file.write(document.decode("utf-8"))
        return

    @staticmethod
    def __write_bad_records_to_log(bad_record):
        with open("bad_records.log", 'a+') as bad_records:
            bad_records.write(f'This is a bad record:\n  {bad_record}\n')
        return


class DCTester:
    def __init__(self, metadata_format, document):
        self.metadata_key = metadata_format
        self.document = document
        self.is_good = self.__test()

    def __test(self):
        has_title = self.__check_for_title()
        has_rights = self.__check_for_rights()
        has_thumbs = self.__check_identifiers()
        if has_rights is True and has_thumbs is True and has_title is True:
            return True
        else:
            return False

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
    def __init__(self, document):
        self.document = document
        self.is_good = self.__test()

    def __test(self):
        has_thumbnails = self.__check_thumbnails()
        return has_thumbnails

    def __check_titles(self):
        return

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
        title_info = self.document['mods']['titleInfo']
        try:
            if type(title_info) is list:
                for title in title_info:
                    if "@type" in title:
                        if title['@type'] != "alternative":
                            has_title = True
                    elif "#text" in title:
                        has_title = True
                    elif type(title) is str:
                        has_title = True
            elif type(title_info) is dict:
                if "@type" in title_info['title']:
                    if title_info['title']['@type'] != "alternative":
                        has_title = True
                elif type(title_info['title']) is str:
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
        return has_object_in_context


if __name__ == "__main__":
    #x = OAIRequest("http://nashville.contentdm.oclc.org/oai/oai.php", "nr", "oai_qdc").list_records()
    x = OAIRequest("http://dlynx.rhodes.edu:8080/oai/request", "col_10267_34285", "xoai")
    x.list_records()
    print(f'Set currently has {x.bad_records} bad records.')

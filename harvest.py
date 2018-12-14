import requests
from lxml import etree
import json
import xmltodict


class OAIRequest:
    def __init__(self, endpoint, oai_set="nr", prefix="oai_dc"):
        self.oai_base = endpoint
        self.endpoint = self.set_endpoint(endpoint, oai_set, prefix)
        self.token = ""
        self.metadata_prefix = prefix
        self.metadata_key = self.__set_metadata_key(prefix)
        self.status = "In Progress"
        self.set = oai_set

    @staticmethod
    def __set_metadata_key(metadata_format):
        if metadata_format == "oai_dc":
            return "oai_dc:dc"
        elif metadata_format == "oai_qdc":
            return "oai_qdc:qualifieddc"

    @staticmethod
    def set_endpoint(our_endpoint, our_set, our_prefix):
        endpoint = f"{our_endpoint}?verb=ListRecords&metadataPrefix={our_prefix}"
        if our_set != "":
            endpoint = f"{endpoint}&set={our_set}"
        return endpoint

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
            record = metadata.findall('.//{http://www.openarchives.org/OAI/2.0/oai_dc/}dc')
            if len(record) != 0:
                for rec in record:
                    record_as_xml = etree.tostring(rec)
                    record_as_json = json.loads(json.dumps(xmltodict.parse(record_as_xml)))
                    has_title = self.__check_for_title(record_as_json)
                    has_rights = self.__check_for_rights(record_as_json)
                    has_url = self.__check_identifiers(record_as_json)
                    print(f"{has_url} {has_title} {has_rights}")
                    if has_rights is True and has_title is True and has_url is True:
                        self.__write_to_disk(record_as_xml, filename)
        return

    @staticmethod
    def __check_for_title(document):
        try:
            if document["oai_dc:dc"]["dc:title"]:
                return True
        except KeyError:
            return False

    @staticmethod
    def __check_for_rights(document):
        try:
            if document["oai_dc:dc"]["dc:rights"]:
                return True
        except KeyError:
            return False

    @staticmethod
    def __check_identifiers(document):
        identifiers = document["oai_dc:dc"]["dc:identifier"]
        try:
            if type(identifiers) is str:
                if identifiers.startswith("http"):
                    return True
                else:
                    return False
            elif type(identifiers) is list:
                good = False
                for id in identifiers:
                    if id.startswith("http"):
                        good = True
                return good
            else:
                return False
        except KeyError:
            return False

    @staticmethod
    def __write_to_disk(document, name):
        filename = name.split(":")[-1].replace("/", "_")
        with open(f"output/{filename}.xml", "w") as xml_file:
            xml_file.write(document.decode("utf-8"))
        return


if __name__ == "__main__":
    OAIRequest("http://digi.countrymusichalloffame.org/oai/oai.php", "musicaudio").list_records()

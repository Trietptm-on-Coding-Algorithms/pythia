from __future__ import print_function
import idaapi
import json

print("[+] Loading RTTI information from JSON file")

with open("output.json", "r") as fh:
    data = json.load(fh)

print("[+] Finished loading, starting to rename")

for item in data["items"]:
    MakeComm(item['va'], item['name'].encode("ascii"))

    # A short Pascal string (1 byte length, ASCII data, no null terminator).
    # Note it seems these can be UTF in modern Delphi, e.g. object names.
    if item["type"] == "p":
        MakeUnknown(item["va"], item["size"], DOUNK_SIMPLE)
        idaapi.make_ascii_string(item["va"], item["size"], ASCSTR_PASCAL)
    
    # 4 byte integer value
    elif item["type"] == "I":
        MakeUnknown(item["va"], item["size"], DOUNK_SIMPLE)
        MakeDword(item["va"])

    # 2 byte integer value
    elif item["type"] == "H":
        MakeUnknown(item["va"], item["size"], DOUNK_SIMPLE)
        MakeWord(item["va"])

    # 1 byte value, either integer or a single byte
    elif item["type"] == "B":
        MakeUnknown(item["va"], item["size"], DOUNK_SIMPLE)
        MakeByte(item["va"])

    # GUID, custom format
    elif item["type"] == "G":
        MakeUnknown(item["va"], item["size"], DOUNK_SIMPLE)
        MakeDword(item["va"])
        MakeWord(item["va"] + 4)
        MakeWord(item["va"] + 6)
        MakeWord(item["va"] + 8)
        MakeData(item["va"] + 10, FF_BYTE, 6, 0)

        comm = "GUID: {}".format(item["data"])
        MakeComm(item['va'], comm)

seen = set()
for item in data["name_hints"]:
    if item["va"] in seen:
        print("Already renamed 0x{:08x}".format(item["va"]))
        comm = Comment(item["va"])
        if comm:
            comm += "\n{}".format(item["name"])
        else:
            comm = item["name"]
        MakeComm(item["va"], str(comm))
        continue
        
    MakeNameEx(item["va"], str(item["name"]), SN_NOWARN)
    seen.add(item["va"])

print("[+] Finished renaming")

# This seems to occasionally crash IDA, figure out why before uncommenting
#idaapi.refresh_strlist(0, 1)

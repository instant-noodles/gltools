import io
import math
import json
import xml.etree.ElementTree as ET

from dataclasses import asdict, fields
from gldc import *
from glutil import GLReader
from os import mkdir
from pathlib import Path
from PIL import Image

def animRead(file):
    print(f"-- Reading {file.name}...")
    try:
        reader=GLReader(file)
        anim=anim_bin()
        anim.magic_num=reader.Str(4)
        fill(anim, 5, reader, [1])

        if anim.magic_num!="ANIM" or anim.version<7:
            raise Exception

        for num in range(anim.num_anims):
            anm=animation()
            fill(anm, 5, reader)
            isFirst=True
            last={"angle": 0, "scale_x": 0, "scale_y": 0}

            for idx in range(anm.num_frames):
                frm=aframe()
                fill(frm, 5, reader)

                for ele in range(frm.num_elements):
                    elt=element()
                    fill(elt, 18, reader)
                    elt.x=elt.mx*1
                    elt.y=elt.my*-1
                    elt.scale_x=math.sqrt(pow(elt.m1, 2)+pow(elt.m2, 2))
                    elt.scale_y=math.sqrt(pow(elt.m3, 2)+pow(elt.m4, 2))
                    det=elt.m1*elt.m4-elt.m3*elt.m2

                    if (det<0):
                        if (isFirst or last["scale_x"]<last["scale_y"]):
                            elt.scale_x*=-1
                            isFirst=False
                        else:
                            elt.scale_y*=-1

                    if (abs(elt.scale_x)<1e-3 or abs(elt.scale_y)<1e-3):
                        elt.angle=last["angle"]
                    else:
                        sin_apx=0.5*(elt.m3/elt.scale_y-elt.m2/elt.scale_x)
                        cos_apx=0.5*(elt.m1/elt.scale_x+elt.m4/elt.scale_y)
                        elt.angle=math.atan2(sin_apx, cos_apx)
                        
                    elt.spin=1 if abs(elt.angle-last["angle"])<=math.pi else -1

                    if (elt.angle<last["angle"]):
                        elt.spin*=-1

                    if (elt.angle<0):
                        elt.angle+=2*math.pi

                    elt.angle*=180/math.pi
                    last["angle"]=elt.angle
                    last["scale_x"]=elt.scale_x
                    last["scale_y"]=elt.scale_y
                    frm.elements.append(elt)
                    
                anm.frames.append(frm)

            anim.anims.append(anm)

        anim.num_refs=reader.Int()

        for num in range(anim.num_refs):
            ref_hash=reader.Int()
            ref_name=reader.GLStr()
            anim.refs[ref_hash]=ref_name

        reader.close()
        print(f"   > Success: {file.name} is valid")
        return asdict(anim)
    except:
        print(f"   > Failed: {file.name} contains invalid data")
        
def buildRead(file):
    print(f"-- Reading {file.name}...")
    try:
        reader=GLReader(file)
        build=build_bin()
        build.magic_num=reader.Str(4)
        fill(build, 6, reader, [1])

        if build.magic_num!="BILD" or build.version<10:
            raise Exception

        for num in range(build.num_textures):
            build.textures.append(reader.GLStr())

        build.flag=reader.Int()

        for num in range(build.num_symbols):
            sym=symbol()
            fill(sym, 4, reader)

            for idx in range(sym.num_frames):
                frm=bframe()
                fill(frm, 11, reader)

                if frm.w==0 or frm.h==0:
                    frm.piv_x=None
                    frm.piv_y=None
                else:
                    x=frm.x_off-frm.w/2
                    y=frm.y_off-frm.h/2
                    frm.piv_x=0-x/frm.w
                    frm.piv_y=1+y/frm.h

                sym.frames.append(frm)

            build.symbols.append(sym)

        build.num_refs=reader.Int()

        for num in range(build.num_refs):
            ref_hash=reader.Int()
            ref_name=reader.GLStr()
            build.refs[ref_hash]=ref_name

        reader.close()
        print(f"   > Success: {file.name} is valid")
        return asdict(build)
    except:
        print(f"   > Failed: {file.name} contains invalid data")

def fill(dc, end, reader, sList=[]):
    for i, f in enumerate(fields(dc)):
        if i==end:
            break

        if len(sList)>0 and (i+1) in sList:
            continue

        setattr(dc, f.name, reader.next(f.type))

def scmlMake(aData, bData, path):
    print(f"-- Creating Spriter file...")
    try:
        aRefs=aData["refs"]
        bRefs=bData["refs"]
        aKeys=[]
        seKeys=[]
        folLookup={}
        seLookup={}
        tlLookup={}
        tlKeys={}
        scml=ET.Element("spriter_data", scml_version="1.0", generator="BrashMonkey Spriter", generator_version="r11")

        for idx, sym in enumerate(bData["symbols"]):
            sym_ref=sym["ref1"]
            sym_name=bRefs[sym_ref] if isinstance(sym_ref, int) else bRefs[str(sym_ref)]
            fol_name=sym_name
            folder=ET.SubElement(scml, "folder", id=str(idx), name=fol_name)

            for frm in sym["frames"]:
                if frm["piv_x"]==None or frm["piv_y"]==None:
                    continue

                fname=fol_name+"/"+sym_name+"-"+str(frm["ndx"])+".png"
                folLookup[sym_name]=[fol_name, idx]
                file=ET.SubElement(folder, "file", id=str(frm["ndx"]), name=fname, width=str(frm["w"]), height=str(frm["h"]), pivot_x=str(frm["piv_x"]), pivot_y=str(frm["piv_y"]))

        for anm in aData["anims"]:
            aKeys.append(anm["name"] if anm["name"]==anm["name2"] else anm["name"]+"-"+anm["name2"])

        for anm in aData["anims"]:
            name=anm["name"] if anm["name"]==anm["name2"] else anm["name"]+"-"+anm["name2"]
            duration=int(anm["framerate"]*(anm["num_frames"]))
            seLookup[name]=[aKeys.index(name), duration]
            eList_anm=[]
            tlFrames={}
            
            for idx, frm in enumerate(anm["frames"]):
                eList=[]
                tlList={}
                
                for ele in frm["elements"]:
                    ele_ref=ele["ref"]
                    ele_name=aRefs[ele_ref] if isinstance(ele_ref, int) else aRefs[str(ele_ref)]
                    tlName=ele_name+"_"+str(int(ele["index"]))

                    if ele_name in aKeys and ele_name not in seKeys:
                        seKeys.append(ele_name)

                    if ele_name in folLookup or ele_name in seKeys:
                        for idx2 in range(10):
                            eRef=ele_name+"-"+str(idx2)
                            
                            if not eRef in eList:
                                eList.append(eRef)
                                break

                        if tlName not in tlKeys:
                            tlList[tlName]=eRef

                tlFrames[idx]=tlList

                for ele in eList:
                    if ele not in eList_anm:
                        eList_anm.append(ele)

            tlLookup[name]=tlFrames
            tlKeys[name]=eList_anm

        root_name=bData["root"]
        entity=ET.SubElement(scml, "entity", id="0", name=root_name)

        for idx, anm in enumerate(aData["anims"]):
            name=anm["name"] if anm["name"]==anm["name2"] else anm["name"]+"-"+anm["name2"]
            rate=anm["framerate"]
            duration=int(rate*anm["num_frames"])
            eleDic={}
            animation=ET.SubElement(entity, "animation", id=str(idx), name=name, length=str(duration), interval="100")
            mainline=ET.SubElement(animation, "mainline")

            for idx2, frm in enumerate(anm["frames"]):
                cur_time=idx2*rate
                key=ET.SubElement(mainline, "key", id=str(idx2), time=str(int(cur_time)), curve_type="instant")
                num_elements=frm["num_elements"]

                if num_elements==0:
                    continue

                for idx3, ele in enumerate(frm["elements"]):
                    ele_ref=ele["ref"]
                    ele_name=aRefs[ele_ref] if isinstance(ele_ref, int) else aRefs[str(ele_ref)]
                    file=ele["ndx"]

                    tlName=ele_name+"_"+str(int(ele["index"]))
                    
                    if tlName not in tlLookup[name][idx2]:
                        continue
                    
                    tlRef=tlLookup[name][idx2][tlName]
                    tl=tlKeys[name].index(tlRef)

                    if ele_name not in folLookup and ele_name not in seLookup:
                        folder=None
                        foldername=None
                    else:
                        object_ref=ET.SubElement(key, "object_ref", id=str(idx3), timeline=str(tl), key=str(idx2), z_index=str(num_elements-idx3))

                        if ele_name in seLookup:
                            folder=-1
                            foldername=-1
                        else:
                            lookup=folLookup[ele_name]
                            folder=lookup[1]
                            foldername=lookup[0]

                    x=str(ele["x"])
                    y=str(ele["y"])
                    scale_x=str(ele["scale_x"])
                    scale_y=str(ele["scale_y"])
                    angle=str(ele["angle"])
                    spin=str(ele["spin"])

                    if tl not in eleDic:
                        eleDic[tl]={}

                    eleDic[tl]["name"]=tlRef
                    eleDic[tl]["eName"]=ele_name
                    eleDic[tl][idx2]={"cur_time": cur_time, "file": file, "folder": folder, "x": x, "y": y, "scale_x": scale_x, "scale_y": scale_y, "angle": angle, "spin": spin}

            for num in eleDic:
                ele_name=eleDic[num]["eName"]
                
                if ele_name in seKeys:
                    timeline=ET.SubElement(animation, "timeline", id=str(num), name=eleDic[num]["name"], object_type="entity")
                else:
                    timeline=ET.SubElement(animation, "timeline", id=str(num), name=eleDic[num]["name"])

                for keyId in eleDic[num]:
                    def getValue(keyValue):
                        outValue=eleDic[num][keyId][keyValue]

                        if keyValue=="cur_time":
                            return str(int(outValue))

                        return str(outValue)

                    if (keyId=="name") or (keyId=="eName") or (getValue("folder")=="None"):
                        continue

                    key=ET.SubElement(timeline, "key", id=str(keyId), time=getValue("cur_time"), spin=getValue("spin"))

                    if ele_name in seLookup:
                        obj=ET.SubElement(key, "object", entity="0", animation=str(seLookup[ele_name][0]), t=str(float(int(getValue("file"))*rate/seLookup[ele_name][1])), x=getValue("x"), y=getValue("y"), scale_x=getValue("scale_x"), scale_y=getValue("scale_y"), angle=getValue("angle"))
                    else:
                        obj=ET.SubElement(key, "object", folder=getValue("folder"), file=getValue("file"), x=getValue("x"), y=getValue("y"), scale_x=getValue("scale_x"), scale_y=getValue("scale_y"), angle=getValue("angle"))

        outfile=path/(root_name+".scml")
        tree=ET.ElementTree(scml)
        tree.write(outfile, encoding="utf-8", xml_declaration=True)
        print(f"   > Success: Created {outfile.name} at {outfile.parent}")
    except:
        print(f"   > Failed: Could not create SCML file")
    
def splice(tData, bData, path):
    print(f"-- Creating images and folders...")
    try:
        for sym in bData["symbols"]:
            sym_name=bData["refs"][sym["ref1"]]
            fol_name=sym_name
            output_directory=path/fol_name

            if not Path(output_directory).exists():
                mkdir(output_directory)

            for frm in sym["frames"]:
                img=Image.open(tData)
                img_w, img_h=img.size
                x1=img_w*frm["u1"]
                y1=img_h*frm["v1"]
                x2=img_w*frm["u2"]
                y2=img_h*frm["v2"]

                if (x1==x2 or y1==y2):
                    continue

                outfile=output_directory/(sym_name+"-"+str(frm["ndx"])+".png")
                img_crop=img.crop((x1, y1, x2, y2))
                img_crop.save(outfile, "PNG")

        print(f"   > Success: Created under {path}")
    except:
        print(f"   > Failed: Could not create one or more images and/or folders")

def texRead(file):
    print(f"-- Reading {file.name}...")
    try:
        with open(file, "rb") as infile:
            magic=infile.read(4)
            disc=infile.read(5)

            if magic==b"KTEX":
                data=infile.read()
            elif b"DDS" in magic:
                infile.seek(0)
                data=infile.read()

        infile.close()
        print(f"   > Success: {file.name} is valid")
        return io.BytesIO(data)
    except:
        print(f"   > Failed: {file.name} contains invalid data")

def main(path_input):
    path_input=Path(path_input).absolute()
    
    if path_input.is_dir():
        boolLookup=["anim.bin", "atlas0.tex", "build.bin"]
        fileBools=[len(list(path_input.glob(boolLookup[x])))>0 for x in range(len(boolLookup))]
        missing=[]
        valid=True

        for idx, fileBool in enumerate(fileBools):
            valid=valid and fileBool

            if not fileBool:
                missing.append(boolLookup[idx])

        if valid:
            path_anim=path_input/boolLookup[0]
            path_tex=path_input/boolLookup[1]
            path_build=path_input/boolLookup[2]

            animData=animRead(path_anim)
            texData=texRead(path_tex)
            buildData=buildRead(path_build)
            splice(texData, buildData, path_input)
            scmlMake(animData, buildData, path_input)
        else:
            missing=", ".join(missing)
            print(f"-- {path_input} does not contain: {missing}")
    else:
        print(f"-- {path_input} either does not exist or is not a directory")

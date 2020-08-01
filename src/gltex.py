import io

from dataclasses import fields
from gldc import pbox
from glutil import GLReader
from pathlib import Path
from PIL import Image

def readMagic(file):
    with open(file, "rb") as infile:
        magic=infile.read(4)
        infile.close()
        
    return magic

def tex2png(file):
    filename=file.name
    outfile=filename.replace(".tex", ".png")
    print(f"-- Converting {filename}...")

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
        image=Image.open(io.BytesIO(data))
        w, h=image.size
        image.save(file.parent/outfile, "PNG")

        print(f"   > Success: Saved {outfile} ({w}x{h}) to {file.parent}")
    except:
        print(f"   > Failed: {filename} contains invalid data")

def plax2png(file):
    filename=file.name
    outfile=filename.replace(".tex", ".png")
    print(f"-- Converting {filename}...")

    try:
        reader=GLReader(file)
        magic=reader.Str(4)
        num_root=reader.Byte()
        w=reader.Int()
        h=reader.Int()
        root=reader.GLBStr()
        num_splice=reader.Int()

        root_split=root.split("/")
        root_name_tex=root_split[len(root_split)-1]
        root_name=root_name_tex.replace(".tex", ".png")
        path_root=file.parent/root_name
        path_root_tex=file.parent/root_name_tex

        if path_root.is_file() or path_root_tex.is_file():
            output_img=Image.new("RGBA", (w, h))

            if not path_root.is_file():
                print(f"   > Missing: {root_name} is required for converting {filename}")
                print(f"   > Will convert {root_name_tex} to {root_name} first")
                tex2png(path_root_tex)
                print(f"-- Converting {filename}...")
            
            for num in range(num_splice):
                p=pbox()

                for f in fields(p):
                    setattr(p, f.name, reader.next(f.type))

                p.n_v1=1-p.n_v1
                p.n_v2=1-p.n_v2

                img_source=Image.open(path_root)
                imgW, imgH=img_source.size

                x1=imgW*p.u1
                y1=imgH*p.v1
                x2=imgW*p.u2
                y2=imgH*p.v2

                img_crop=img_source.crop((x1,y1,x2,y2))
                bbox=[p.n_u1*w, p.n_v1*h, p.n_u2*w, p.n_v2*h]
                bbox=[int(i-0.5) for i in bbox]
                bboxW=(bbox[2]-bbox[0])
                bboxH=(bbox[3]-bbox[1])

                xdiff=round(x2-x1)
                ydiff=round(y2-y1)
                xnew=xdiff
                ynew=ydiff

                if (bboxW!=xdiff):
                    if (bboxW-xdiff<2):
                        bbox[2]+=round((x2-x1)-bboxW)
                    else:
                        xnew=bboxW

                if (bboxH!=ydiff):
                    if (bboxH-ydiff<2):
                        bbox[3]+=round((y2-y1)-bboxH)
                    else:
                        ynew=bboxH

                if (xnew!=xdiff or ynew!=ydiff):
                    img_crop=img_crop.resize((xnew, ynew))

                output_img.paste(img_crop, bbox)

            output_img.save(file.parent/outfile, "PNG")
            reader.close()
            
            print(f"   > Success: Saved {outfile} ({w}x{h}) to {file.parent}")
        else:
            print(f"   > Failed: {root_name_tex} or {root_name} is required")
    except:
        print(f"   > Failed: {filename} contains invalid data")
    
def main(path_input):
    path_input=Path(path_input).absolute()
    
    if path_input.is_file():
        magic=readMagic(path_input)

        if magic==b"KTEX" or b"DDS" in magic:
            tex2png(path_input)
        elif magic==b"PLAX":
            plax2png(path_input)
        else:
            print(f"-- Converting {path_input.name}...")
            print("   > Skipped: Not a valid Griftlands .tex file")
    elif path_input.is_dir():
        files=list(path_input.glob("*.tex"))

        texList=[]
        plaxList=[]

        for file in files:
            magic=readMagic(file)

            if magic==b"KTEX" or b"DDS" in magic:
                texList.append(file)
            elif magic==b"PLAX":
                plaxList.append(file)
            else:
                print(f"-- Converting {file.name}...")
                print("   > Skipped: Not a valid Griftlands .tex file")

        for file in texList:
            tex2png(file)

        for file in plaxList:
            plax2png(file)

        if (len(texList)==0 and len(plaxList)==0):
            print(f"-- {path_input} does not contain any Griftlands .tex files")
    else:
        print(f"-- {path_input} does not exist")

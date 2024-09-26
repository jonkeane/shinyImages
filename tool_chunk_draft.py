@tool(parse_docstring=True)
def exiftool(url: Annotated[str, InjectedToolArg]) -> str:
    """extract exif data

    Args:
        url: url of the image.
    """
    return """
ExifTool Version Number         : 12.97
File Name                       : 50302524873_18a99d6974_b.jpg
Directory                       : /Users/jkeane/Downloads
File Size                       : 143 kB
File Modification Date/Time     : 2024:09:25 07:58:16-05:00
File Access Date/Time           : 2024:09:25 20:53:40-05:00
File Inode Change Date/Time     : 2024:09:25 07:58:16-05:00
File Permissions                : -rw-r--r--
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
Exif Byte Order                 : Big-endian (Motorola, MM)
Artist                          : Jonathan Keane
Copyright                       : All rights reserved
Current IPTC Digest             : d000166aa26947dcc219dc361815c38b
Coded Character Set             : UTF8
Envelope Record Version         : 4
Document Notes                  : https://flickr.com/e/bcl5xB5UvnfuXZGu8ZhTmJaTAGmnvAiSpOPHG54L6us%3D, Email:jkeane@gmail.com, URL:jonkeane.com
Copyright Notice                : All rights reserved
By-line                         : Jonathan Keane
Application Record Version      : 4
JFIF Version                    : 1.02
Resolution Unit                 : None
X Resolution                    : 1
Y Resolution                    : 1
Profile CMM Type                : Linotronic
Profile Version                 : 2.1.0
Profile Class                   : Display Device Profile
Color Space Data                : RGB
Profile Connection Space        : XYZ
Profile Date Time               : 1998:02:09 06:49:00
Profile File Signature          : acsp
Primary Platform                : Microsoft Corporation
CMM Flags                       : Not Embedded, Independent
Device Manufacturer             : Hewlett-Packard
Device Model                    : sRGB
Device Attributes               : Reflective, Glossy, Positive, Color
Rendering Intent                : Perceptual
Connection Space Illuminant     : 0.9642 1 0.82491
Profile Creator                 : Hewlett-Packard
Profile ID                      : 0
Profile Copyright               : Copyright (c) 1998 Hewlett-Packard Company
Profile Description             : sRGB IEC61966-2.1
Media White Point               : 0.95045 1 1.08905
Media Black Point               : 0 0 0
Red Matrix Column               : 0.43607 0.22249 0.01392
Green Matrix Column             : 0.38515 0.71687 0.09708
Blue Matrix Column              : 0.14307 0.06061 0.7141
Device Mfg Desc                 : IEC http://www.iec.ch
Device Model Desc               : IEC 61966-2.1 Default RGB colour space - sRGB
Viewing Cond Desc               : Reference Viewing Condition in IEC61966-2.1
Viewing Cond Illuminant         : 19.6445 20.3718 16.8089
Viewing Cond Surround           : 3.92889 4.07439 3.36179
Viewing Cond Illuminant Type    : D50
Luminance                       : 76.03647 80 87.12462
Measurement Observer            : CIE 1931
Measurement Backing             : 0 0 0
Measurement Geometry            : Unknown
Measurement Flare               : 0.999%
Measurement Illuminant          : D65
Technology                      : Cathode Ray Tube Display
Red Tone Reproduction Curve     : (Binary data 2060 bytes, use -b option to extract)
Green Tone Reproduction Curve   : (Binary data 2060 bytes, use -b option to extract)
Blue Tone Reproduction Curve    : (Binary data 2060 bytes, use -b option to extract)
DCT Encode Version              : 100
APP14 Flags 0                   : [14], Encoded with Blend=1 downsampling
APP14 Flags 1                   : (none)
Color Transform                 : YCbCr
Image Width                     : 1024
Image Height                    : 683
Encoding Process                : Baseline DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:4:4 (1 1)
Image Size                      : 1024x683
Megapixels                      : 0.699
"""

model = model.bind_tools([exiftool])

# inside the function itself

        first = True
        async for chunk in stream:
            if first:
                gathered = chunk
                first = False
            else:
                gathered = gathered + chunk

        for tool_call in gathered.tool_calls:
            tool_call["args"]["url"] = input.url()
            selected_tool = {"exiftool": exiftool}[tool_call["name"].lower()]
            tool_output = selected_tool.invoke(tool_call["args"])
            await chat.append_message(ToolMessage(tool_output, tool_call_id=tool_call["id"]))
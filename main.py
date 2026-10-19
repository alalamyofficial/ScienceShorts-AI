import asyncio, json, os, random, re, subprocess, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts

ROOT = Path(__file__).parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
W, H = 1080, 1920
VOICE = os.getenv("TTS_VOICE", "en-US-AriaNeural")

# Small starter bank of fact-checkable evergreen facts. Expand only after checking reputable sources.
FACTS = [
 {"id":"space_001", "title":"A Day on Venus Is Longer Than Its Year", "hook":"Imagine a planet where one day lasts longer than an entire year.", "body":"Venus rotates incredibly slowly. One complete rotation takes about 243 Earth days. But Venus travels around the Sun in about 225 Earth days. That means a Venus day, measured by one full rotation relative to the stars, is longer than its year. Venus also rotates in the opposite direction to most planets, so the Sun would appear to rise in the west and set in the east. Scientists study Venus to understand how a rocky planet can develop such extreme temperatures and a thick atmosphere. It is a powerful reminder that a day on another world can mean something very different from a day on Earth.", "source":"NASA Solar System Exploration: Venus (https://science.nasa.gov/venus/)"},
 {"id":"ocean_001", "title":"The Ocean Has Underwater Waterfalls", "hook":"Earth has waterfalls hidden beneath the ocean surface.", "body":"They are not waterfalls in the usual sense, because the water does not fall through open air. Instead, differences in temperature and saltiness make some seawater denser than nearby water. The denser water can flow down the ocean floor and over underwater slopes, forming powerful cascading currents. One famous example is the Denmark Strait cataract between Greenland and Iceland. It is considered one of the largest waterfalls on Earth by water volume, even though it happens entirely underwater. These currents help move heat, oxygen, and nutrients around the planet. The ocean is not still at all: it is full of hidden rivers and moving layers that shape Earth's climate.", "source":"NOAA Ocean Exploration (https://oceanexplorer.noaa.gov/)"},
 {"id":"biology_001", "title":"Octopuses Have Three Hearts", "hook":"An octopus has three hearts, and its blood is blue.", "body":"Two of its hearts pump blood toward the gills, where oxygen is absorbed. The third heart pumps oxygen-rich blood to the rest of the body. Octopus blood looks blue because it uses a copper-containing molecule called hemocyanin to carry oxygen, rather than the iron-containing hemoglobin found in human blood. Hemocyanin works well in cold, low-oxygen environments, which helps many cephalopods survive in the sea. There is another surprising detail: when an octopus swims, the heart that supplies the body temporarily stops beating, which is one reason crawling can be less tiring than swimming. These animals are full of unusual adaptations that scientists are still investigating.", "source":"Smithsonian Ocean (https://ocean.si.edu/)"},
 {"id":"space_002", "title":"A Neutron Star Is Incredibly Dense", "hook":"A tiny amount of a neutron star would weigh an astonishing amount on Earth.", "body":"Neutron stars form when certain massive stars explode and their cores collapse. They can pack more mass than the Sun into a sphere only about the size of a city. Matter inside is compressed to densities far beyond anything we can create in an ordinary laboratory. Popular science often describes a teaspoon of neutron-star material as weighing billions of tons, but the exact comparison depends on the star and the assumptions used. We cannot scoop up such material and bring it home; under Earth's conditions it would not remain in the same state. Neutron stars help researchers test physics under extreme gravity, density, and magnetic fields.", "source":"NASA: Neutron Stars (https://science.nasa.gov/universe/stars/neutron-stars/)"},
 {"id":"plants_001", "title":"Plants Can Send Chemical Warning Signals", "hook":"Some plants can warn nearby plants that danger is close.", "body":"When certain plants are attacked by insects, they release airborne chemicals. Nearby plants can detect some of these compounds and change their own defenses. The response varies by species and environment, and scientists continue to study how often these signals provide a real benefit in nature. Plants do not speak or think like humans, but they constantly respond to chemical, light, touch, and water cues. Underground, roots and soil microbes also interact in complex ways. The result is a living environment where organisms affect one another without needing a nervous system. Plant communication is a useful reminder that biology has many ways to exchange information.", "source":"Royal Society / plant volatile signalling research (https://royalsocietypublishing.org/)"},
 {"id":"physics_001", "title":"Lightning Is Hotter Than the Sun's Surface", "hook":"A lightning channel can briefly become hotter than the surface of the Sun.", "body":"A lightning strike heats the air along its path to roughly thirty thousand kelvin for a very short time. The Sun's visible surface is around five thousand eight hundred kelvin. That makes the air in a lightning channel several times hotter than the Sun's surface, although the comparison is about temperature, not total energy or size. The sudden heating makes air expand explosively, creating the shock wave we hear as thunder. Lightning is brief, unpredictable, and dangerous, so it should never be approached or used for experiments. It is also a dramatic example of how electrical energy can rapidly transform the atmosphere.", "source":"NOAA National Severe Storms Laboratory (https://www.nssl.noaa.gov/education/svrwx101/lightning/)"},
 {"id":"space_003", "title":"Footprints on the Moon Can Last a Long Time", "hook":"Some astronaut footprints on the Moon may remain for millions of years.", "body":"The Moon has no wind or rain like Earth, so there is no weather to quickly erase tracks left on its surface. The fine lunar dust can preserve footprints and rover tracks for a very long time. They will not last forever: micrometeorite impacts and other space-weathering processes gradually disturb the surface. But without Earth's familiar erosion, changes happen much more slowly. The Apollo landing sites still preserve evidence of human exploration, and spacecraft images have documented trails left by astronauts and equipment. The Moon is a natural archive, recording impacts and activity over immense spans of time. It also reminds us how different two neighboring worlds can be.", "source":"NASA Apollo Lunar Surface Journal / NASA Moon resources (https://science.nasa.gov/moon/)"},
 {"id":"animal_001", "title":"Wombats Produce Cube-Shaped Poop", "hook":"One mammal is famous for producing cube-shaped droppings: the wombat.", "body":"Wombats are Australian marsupials, and their droppings can have a distinct cube-like shape. Research suggests the shape develops inside the intestine, where regions of different stiffness help form relatively sharp edges as material dries. The cubes may be useful for marking territory because they are less likely to roll away from rocks and other raised spots. Scientists studied this unusual process by examining intestinal tissue and the mechanics involved. It is a strange but real example of how anatomy and physics can combine to produce a surprising result. Nature is full of adaptations that seem unbelievable until researchers investigate how they work.", "source":"Peer-reviewed research in Soft Matter (2018), wombat feces formation"},
 {"id":"earth_001", "title":"Earth Is Not a Perfect Sphere", "hook":"Earth is slightly squashed at the poles and wider at the equator.", "body":"Earth's rotation creates a small outward effect around the equator. Over geological time, this contributes to an equatorial bulge, so our planet is an oblate spheroid rather than a perfect sphere. The equatorial radius is about twenty-one kilometers larger than the polar radius. Mountains, ocean trenches, and variations in density also make Earth's shape more complicated than a simple smooth ball. Scientists describe the real gravity-related shape using a concept called the geoid. This matters for precise navigation, satellite measurements, and understanding sea level. Even a planet that looks round from space has subtle irregularities when measured carefully.", "source":"NASA Earth Observatory (https://earthobservatory.nasa.gov/)"}
]


def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for f in candidates:
        if Path(f).exists(): return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def make_background(fact, path, seed):
    random.seed(seed)
    img = Image.new("RGB", (W,H))
    px = img.load()
    c1 = (8, 18, 48); c2 = (26, 75, 105)
    for y in range(H):
        t = y / H
        c = tuple(int(c1[i]*(1-t) + c2[i]*t) for i in range(3))
        for x in range(W): px[x,y] = c
    d = ImageDraw.Draw(img, "RGBA")
    # Decorative science orbits and particles, generated locally (no image API required)
    for i in range(18):
        x = random.randint(-100, W+100); y = random.randint(100, H-100)
        r = random.randint(8, 42)
        d.ellipse((x-r,y-r,x+r,y+r), outline=(100,220,255,70), width=random.randint(2,5))
    d.ellipse((W//2-250, 330, W//2+250, 830), outline=(90,225,255,110), width=5)
    d.ellipse((W//2-110, 470, W//2+110, 690), fill=(70,190,235,35), outline=(180,245,255,180), width=4)
    # header
    d.rounded_rectangle((60,80,W-60,160), radius=28, fill=(0,0,0,75), outline=(120,220,255,140), width=2)
    d.text((W//2,120), "SCIENCE IN 60 SECONDS", font=font(30,True), fill=(190,240,255), anchor="mm")
    # title
    words = fact["title"].split(); lines=[]; line=""
    f=font(62,True)
    for word in words:
        test=(line+" "+word).strip()
        if d.textbbox((0,0),test,font=f)[2] > W-140:
            lines.append(line); line=word
        else: line=test
    if line: lines.append(line)
    yy=900
    for line in lines[:4]:
        d.text((W//2,yy), line, font=f, fill="white", anchor="mm", stroke_width=2, stroke_fill=(0,0,0,100)); yy += 82
    d.rounded_rectangle((90,1250,W-90,1425), radius=30, fill=(0,0,0,75), outline=(120,220,255,100), width=2)
    d.text((W//2,1305), "THE UNIVERSE IS STRANGER", font=font(28,True), fill=(125,230,255), anchor="mm")
    d.text((W//2,1360), "THAN YOU THINK", font=font(28,True), fill=(125,230,255), anchor="mm")
    d.text((W//2,H-110), "Follow for more science facts", font=font(28), fill=(230,245,255), anchor="mm")
    img.save(path, quality=94)


def srt_time(seconds):
    ms=int((seconds-int(seconds))*1000); s=int(seconds); h=s//3600; m=(s%3600)//60; sec=s%60
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"


def make_srt(text, duration, path):
    # Captions are timed approximately by word count; review before publishing.
    words=text.split(); chunks=[]
    for i in range(0,len(words),8): chunks.append(" ".join(words[i:i+8]))
    weights=[max(1,len(c.split())) for c in chunks]; total=sum(weights); t=0; out=[]
    for idx,(chunk,w) in enumerate(zip(chunks,weights),1):
        start=t; t += duration*w/total
        out.append(f"{idx}\n{srt_time(start)} --> {srt_time(min(duration,t))}\n{chunk}\n")
    path.write_text("\n".join(out), encoding="utf-8")

async def generate_video(fact, idx):
    slug=f"{idx:02d}_{fact['id']}"
    mp3=OUT/f"{slug}.mp3"; bg=OUT/f"{slug}_background.jpg"; srt=OUT/f"{slug}.srt"; mp4=OUT/f"{slug}.mp4"
    narration=f"{fact['hook']} {fact['body']} The key lesson is that real science is often stranger than fiction. Check the source listed with this video, and follow for more carefully researched science facts. Share this with someone who loves learning."
    communicate=edge_tts.Communicate(narration, VOICE, rate="-8%")
    await communicate.save(str(mp3))
    probe=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(mp3)],capture_output=True,text=True,check=True)
    duration=float(probe.stdout.strip())
    make_background(fact,bg,idx)
    make_srt(narration,duration,srt)
    # Slow zoom on a locally generated visual; subtitles burned into output.
    vf=("scale=1080:1920,zoompan=z='min(zoom+0.00025,1.04)':d=1:s=1080x1920:fps=30,"
        f"subtitles='{srt.as_posix()}':force_style='FontName=DejaVu Sans,FontSize=13,PrimaryColour=&H00FFFFFF,OutlineColour=&H00101010,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=190'")
    cmd=["ffmpeg","-y","-loop","1","-i",str(bg),"-i",str(mp3),"-vf",vf,"-t",str(duration),"-r","30","-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-shortest",str(mp4)]
    subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    metadata={"id":fact["id"],"title":fact["title"],"caption":fact["title"]+" #Science #LearnOnTikTok","source":fact["source"],"duration_seconds":round(duration,1),"file":mp4.name,"ai_generated":True}
    (OUT/f"{slug}.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    return metadata

async def main():
    # Deterministic daily rotation: each run picks 3 different facts based on UTC date.
    from datetime import datetime, timezone
    day=int(datetime.now(timezone.utc).strftime("%Y%m%d"))
    start=(day*7)%len(FACTS)
    selected=[FACTS[(start+i)%len(FACTS)] for i in range(3)]
    results=[]
    for i,fact in enumerate(selected,1):
        print(f"Generating {i}/3: {fact['title']}")
        results.append(await generate_video(fact,i))
    (OUT/"manifest.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    print("Done. Review output/*.mp4 and output/manifest.json before publishing.")

if __name__=="__main__":
    asyncio.run(main())

"""Pasta bot command"""

import random

from typing import Optional

from sadbot.commands.interface import CommandsInterface
from sadbot.message import Message


class PastaBotCommand(CommandsInterface):
    """This is the pasta bot command class"""

    @property
    def command_regex(self) -> str:
        """Returns the regex for matching pasta commands"""
        return r"((!|\.)([Pp][Aa][Ss][Tt][Aa])).*"

    @property
    def parsemode(self) -> Optional[str]:
        """Returns the command parsemode"""
        return None

    def get_reply(self, message: Optional[Message] = None) -> Optional[str]:
        """Returns a pasta"""
        pastas = {
            "marine": """What the fuck did you just fucking say about me, you little bitch? I'll have you know I graduated top of my class in the Navy Seals, and I've been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills. I am trained in gorilla warfare and I'm the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with saying that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You're fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that's just with my bare hands. Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little "clever" comment was about to bring down upon you, maybe you would have held your fucking tongue. But you couldn't, you didn't, and now you're paying the price, you goddamn idiot. I will shit fury all over you and you will drown in it. You're fucking dead, kiddo.""",
            "china": """动态网自由门 天安門 天安门 法輪功 李洪志 Free Tibet 六四天安門事件 The Tiananmen Square protests of 1989 天安門大屠殺 The Tiananmen Square Massacre 反右派鬥爭 The Anti-Rightist Struggle 大躍進政策 The Great Leap Forward 文化大革命 The Great Proletarian Cultural Revolution 人權 Human Rights 民運 Democratization 自由 Freedom 獨立 Independence 多黨制 Multi-party system 台灣 臺灣 Taiwan Formosa 中華民國 Republic of China 西藏 土伯特 唐古特 Tibet 達賴喇嘛 Dalai Lama 法輪功 Falun Dafa 新疆維吾爾自治區 The Xinjiang Uyghur Autonomous Region 諾貝爾和平獎 Nobel Peace Prize 劉暁波 Liu Xiaobo 民主 言論 思想 反共 反革命 抗議 運動 騷亂 暴亂 騷擾 擾亂 抗暴 平反 維權 示威游行 李洪志 法輪大法 大法弟子 強制斷種 強制堕胎 民族淨化 人體實驗 肅清 胡耀邦 趙紫陽 魏京生 王丹 還政於民 和平演變 激流中國 北京之春 大紀元時報 九評論共産黨 獨裁 專制 壓制 統一 監視 鎮壓 迫害 侵略 掠奪 破壞 拷問 屠殺 活摘器官 誘拐 買賣人口 遊進 走私 毒品 賣淫 春畫 賭博 六合彩 天安門 天安门 法輪功 李洪志 Winnie the Pooh 劉曉波动态网自由门""",
            "gnu": """I'd just like to interject for a moment. What you're referring to as Linux, is in fact, GNU/Linux, or as I've recently taken to calling it, GNU plus Linux. Linux is not an operating system unto itself, but rather another free component of a fully functioning GNU system made useful by the GNU corelibs, shell utilities and vital system components comprising a full OS as defined by POSIX.

Many computer users run a modified version of the GNU system every day, without realizing it. Through a peculiar turn of events, the version of GNU which is widely used today is often called "Linux", and many of its users are not aware that it is basically the GNU system, developed by the GNU Project.

There really is a Linux, and these people are using it, but it is just a part of the system they use. Linux is the kernel: the program in the system that allocates the machine's resources to the other programs that you run. The kernel is an essential part of an operating system, but useless by itself; it can only function in the context of a complete operating system. Linux is normally used in combination with the GNU operating system: the whole system is basically GNU with Linux added, or GNU/Linux. All the so-called "Linux" distributions are really distributions of GNU/Linux.""",
            "arab": """الامهات الساخنة كبيرة في منطقتك الرغبة في ممارسة الجنس Fortnite free download 16GB 32bit الله

أحب ستيفانيPunjabi Movie 2016 HD.mp4""",
            "coma": """IF YOU'RE READING THIS, YOU'VE BEEN IN A COMA FOR ALMOST 20 YEARS NOW. WE'RE TRYING A NEW TECHNIQUE. WE DON'T KNOW WHERE THIS MESSAGE WILL END UP IN YOUR DREAM, BUT WE HOPE WE'RE GETTING THROUGH.""",
            "russia": """forgive english, i am Russia.

i come to study clothing and fashion at American university. i am here little time and i am very hard stress. i am gay also and this very difficult for me, i am very religion person. i never act to be gay with other men before. but after i am in america 6 weeks i am my friend together he is gay also. He was show me American fashion and then we are kiss.

We sex together. I never before now am tell my mother about gay because i am very shame. As i fock this American boy it is very good to me but also i am feel so guilty. I feel extreme guilty as I begin orgasm. I feel so guilty that I pick up my telephone and call Mother in Russia. I awaken her. It too late for stopping so I am cumming sex. I am very upset and guilty and crying, so I yell her, "I AM CUM FROM SEX" (in Russia). She say what? I say "I AM CUM FROM SEX" and she say you boy, do not marry American girl, and I say "NO I AM CUM FROM SEX WITH MAN, I AM IN ASS, I CUM IN ASS" and my mother very angry me. She not get scared though.

I hang up phone and am very embarrass. My friend also he is very embarrass. I am guilt and feel very stupid. I wonder, why do I gay with man? But I continue because when it spurt it feel very good in American ass.""",
            "helicopter": """I sexually Identify as an Attack Helicopter. Ever since I was a boy I dreamed of soaring over the oilfields dropping hot sticky loads on disgusting foreigners. People say to me that a person being a helicopter is Impossible and I’m fucking retarded but I don’t care, I’m beautiful. I’m having a plastic surgeon install rotary blades, 30 mm cannons and AMG-114 Hellfire missiles on my body. From now on I want you guys to call me “Apache” and respect my right to kill from above and kill needlessly. If you can’t accept me you’re a heliphobe and need to check your vehicle privilege. Thank you for being so understanding.""",
            "anomalous": """We are anomalous
We are region
Forgive and forget
Expecto patronum""",
            "daddy": """Daddy’s 🧔 cummies, 💦 nice 😊 and yummy 😋 Thick 😫👌and gooey, feel like honey 🍯 That sweet 🍭 milk, 🥛 oh-so-tasty 🤤 Daddy, 🧔 Daddy, 🧔 please be hasty!💨 My tongue 👅 swirls 😛 round 🔁 and round 🔁 While Daddy 🧔 gives my ass 🍑 a great big pound 🤜💥 Over 😑 in the corner, wrapped 🎁 in chains ⛓ Mommy 👩 huddled over, screaming 😱 in pain 😪 “Shut up, bitch! 👩 Stay on the floor!” Mommy 👩 sobbing 😭 louder, I 👧 call 🗣 her a whore She reaches behind her 👩 for her gun 💀 While Daddy gropes 👋 and tickles 🤗 my sweet 🍬 buns 🍑 Puts the barrel 😛 between 👉👈 her teeth 👄 And Daddy’s 🧔 semen 💦 begins to seep ☔️ Gunpowder, blood, 💉 brains 🧠 and gore 😎 Mommy’s 👩 lifeless 👻 corpse slumps ⬇️ to the floor 😂 Cummies, 💦 cummies 💦 filling my throat My pussy 🐱 is completely 😍 soaked 💦 But Daddy’s cock 🍆 just gets bigger 😳😲 Over near 😯 the drawers, he grabs the scissors ✂️ Cuts 🔪 a hole 🕳 in Mommy’s 👩 stomach In her hand, 🤲 a gin and tonic 🍺 He 🧔 begins to unravel her strings of intestines 😝 “Look 👀 closely, you’ll learn 👨‍🏫 a lesson” Ties a noose, 😔 rigs it tight 😫 “Sweetie, 👧 sweetie, 👧 no need to fight” 👊💥 Puts her 👩 guts 🤤 around 🔄 my neck “Looks like everything’s good 👍 and set” 👌 Lets me fall down ⬇️ about 🤔💭 a yard Face 👧 turning blue, choking 🤭 hard 💪 All the while, 🕑 Daddy’s 🧔 stroking his cock 🍆 And for a moment, 😳 our eyes 👁 lock 🔒 Tears 😭 of joy 😊 stream down my face 👧 I’m going to 😵 a better ✨ place~""",
            "15": """Number 15

Burger King Foot Lettuce. The last thing you’d want in your Burger King Burger is someone’s foot fungus. But as it turns out that might be what you get. A 4chaner uploaded a photo anonymously to the site showcasing his feet in a plastic bin of lettuce. With the statement “This is the lettuce you eat at Burger King.” Admittedly he had shoes on, but that’s even worse. The post went live at 11:38 pm on July 16 and a mere 20 minutes later the burger king in question was alerted to the rogue employee, at least I hope he’s rogue. How did it happen? Well, the BK employee hadn’t removed the exif data from the uploaded photo, which suggested the culprit was somewhere in Mayfield Heights, Ohio. This was at 11:47. 3 minutes later, at 11:50, the Burger King address was posted, with wishes of happy unemployment. 5 minutes later, the news station was contacted by another 4channer. And 3 minutes later, at 11:58, a link was posted. BK’s “Tell Us About Us” online form. The foot photo, otherwise known as Exhibit A, was attached. Cleveland Scene Magazine contacted the BK in question the next day. When questioned, the breakfast shift manager said, “Oh, I know who that is. He’s getting fired.” Mystery, solved, by4 chan, now we can all go back to eating our fast food in peace.""",
            "b8": """Gr8 b8, m8. I rel8, str8 appreci8, and congratul8. I r8 this b8 an 8/8. Plz no h8, I’m str8 ir8. Cre8 more, can’t w8. We should convers8, I won’t ber8, my number is 8888888, ask for N8. No calls l8 or out of st8. If on a d8, ask K8 to loc8. Even with a full pl8, I always have time to communic8 so don’t hesit8""",
            "leader": """Dear 4chan, It's us, Anonymous, once again. Except this time it's the leader speaking. We are finished with your child pornography, gore, and cruel jokes that spread like a snakes bite and ruin the internet. Where have all of the internet's problems come from? Reddit? Infchan? 9gag? No, no.Here. Tomorrow at 01:00 (4chan Time), Your Website will officially come to an end. "kek u cant do sh*t" Not only do I have my hacking skills and team aside me, but I also have 9gag, the founding website of Anonymous, aside us. You're probably all thinking "DARNIT GUYS WHAT DO WE DO" There is one thing you CAN do. Surrender. I want Moot and Gookmoot here, apologizing and everything, saying sorry, and banning all of these disgusting things from your website. As of now, you have 5 hours. The clock is ticking, gentlemen. We are legion. We do not forgive. We do not forget.""",
        }
        key = None
        if len(message.text) > 7:
            key = message.text[7:]
        if key is not None and key in pastas:
            return pastas[key]
        return random.choice(list(pastas.values()))

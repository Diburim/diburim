/* Opening of the Diburim Shulchan Aruch library.
   Siman 1 of Orach Chaim carries Hebrew of the Mechaber and the Rema
   and a working English translation. Other simanim are shelved so the
   navigation can grow without pretending the work is already done.
   Commentary panels are empty on purpose. */
window.DIBURIM_SHULCHAN = {
  commentaries: {
    "orach-chaim": ["Taz", "Magen Avraham", "Beur HaGra", "Ba'er Heitev", "Shaarei Teshuva", "Mishnah Berurah", "Kaf HaChaim"],
    "yoreh-deah": ["Taz", "Shach", "Beur HaGra", "Pischei Teshuva", "Ba'er Heitev", "Rabbi Akiva Eiger", "Kaf HaChaim"],
    "even-haezer": ["Chelkat Mechokek", "Beit Shmuel", "Beur HaGra", "Pischei Teshuva", "Ba'er Heitev"],
    "choshen-mishpat": ["Taz", "Shach", "Sefer Meirat Einayim", "Ketzot HaChoshen", "Netivot HaMishpat", "Beur HaGra", "Pischei Teshuva", "Ba'er Heitev", "Rabbi Akiva Eiger"]
  },
  chalakim: [
    {
      id: "orach-chaim",
      name: "Orach Chaim",
      hebrew: "אוֹרַח חַיִּים",
      count: 697,
      blurb: "Daily life: rising, prayer, Shabbat, and the festivals.",
      outline: [
        { n: 1, he: "דִּין הַשְׁכָּמַת הַבֹּקֶר", en: "Rising in the morning", seifim: 9, open: true },
        { n: 2, he: "דִּין לְבִישַׁת בְּגָדִים", en: "Getting dressed", seifim: 6 },
        { n: 3, he: "דִּין הַנְהָגַת בֵּית הַכִּסֵּא", en: "Conduct in the privy", seifim: 17 },
        { n: 4, he: "דִּינֵי נְטִילַת יָדַיִם", en: "Washing the hands", seifim: 23 },
        { n: 5, he: "דִּין כַּוָּנַת הַבְּרָכוֹת", en: "Intention in blessings", seifim: 1 },
        { n: 6, he: "בִּרְכַּת אֲשֶׁר יָצַר וֶאֱלֹהַי נְשָׁמָה", en: "Asher Yatzar and Elokai Neshama", seifim: 4 },
        { n: 7, he: "אֲשֶׁר יָצַר כָּל הַיּוֹם", en: "Asher Yatzar through the day", seifim: 4 },
        { n: 46, he: "דִּינֵי בִּרְכוֹת הַשַּׁחַר", en: "The morning blessings", seifim: 9 },
        { n: 47, he: "דִּינֵי בִּרְכַּת הַתּוֹרָה", en: "The blessing of the Torah", seifim: 14 }
      ]
    },
    {
      id: "yoreh-deah",
      name: "Yoreh De'ah",
      hebrew: "יוֹרֶה דֵעָה",
      count: 403,
      blurb: "Kashrut, vows, mourning, and much of the law that orders a Jewish house.",
      outline: []
    },
    {
      id: "even-haezer",
      name: "Even HaEzer",
      hebrew: "אֶבֶן הָעֵזֶר",
      count: 178,
      blurb: "Marriage, the ketubah, and divorce.",
      outline: []
    },
    {
      id: "choshen-mishpat",
      name: "Choshen Mishpat",
      hebrew: "חֹשֶׁן מִשְׁפָּט",
      count: 427,
      blurb: "Courts, testimony, loans, guardians, and the repair of loss.",
      outline: []
    }
  ],
  texts: {
    "orach-chaim/1": {
      title: "Rising in the morning",
      hebrew: "דִּין הַשְׁכָּמַת הַבֹּקֶר",
      intro: "Nine se'ifim. Hebrew follows the standard printed Shulchan Aruch. English is a working Diburim translation, open to revision. It is not a ruling.",
      seifim: [
        {
          n: 1,
          mechaberHe: "יִתְגַּבֵּר כַּאֲרִי לַעֲמוֹד בַּבֹּקֶר לַעֲבוֹדַת בּוֹרְאוֹ, שֶׁיְּהֵא הוּא מְעוֹרֵר הַשַּׁחַר.",
          mechaberEn: "One should strengthen himself like a lion to rise in the morning for the service of his Creator, so that he himself awakens the dawn.",
          remaHe: "וְעַל כָּל פָּנִים לֹא יְאַחֵר זְמַן הַתְּפִלָּה שֶׁהַצִּבּוּר מִתְפַּלְּלִים. שִׁוִּיתִי ה' לְנֶגְדִּי תָמִיד הוּא כְּלָל גָּדוֹל בַּתּוֹרָה וּבְמַעֲלוֹת הַצַּדִּיקִים אֲשֶׁר הוֹלְכִים לִפְנֵי הָאֱלֹהִים. כִּי אֵין יְשִׁיבַת הָאָדָם וּתְנוּעוֹתָיו וַעֲסָקָיו וְהוּא לְבַדּוֹ בְּבֵיתוֹ, כִּישִׁיבָתוֹ וּתְנוּעוֹתָיו וַעֲסָקָיו וְהוּא לִפְנֵי מֶלֶךְ גָּדוֹל. וְלֹא דִּבּוּרוֹ וְהַרְחָבַת פִּיו כִּרְצוֹנוֹ וְהוּא עִם אַנְשֵׁי בֵיתוֹ וּקְרוֹבָיו, כְּדִבּוּרוֹ בְּמוֹשַׁב הַמֶּלֶךְ. כָּל שֶׁכֵּן כְּשֶׁיָּשִׂים הָאָדָם אֶל לִבּוֹ שֶׁהַמֶּלֶךְ הַגָּדוֹל הַקָּדוֹשׁ בָּרוּךְ הוּא, אֲשֶׁר מְלֹא כָל הָאָרֶץ כְּבוֹדוֹ, עוֹמֵד עָלָיו וְרוֹאֶה בְּמַעֲשָׂיו, כְּמוֹ שֶׁנֶּאֱמַר אִם יִסָּתֵר אִישׁ בַּמִּסְתָּרִים וַאֲנִי לֹא אֶרְאֶנּוּ נְאֻם ה', מִיָּד יַגִּיעַ אֵלָיו הַיִּרְאָה וְהַהַכְנָעָה בְּפַחַד ה' וּבוּשָׁתוֹ מִמֶּנּוּ תָּמִיד. וְלֹא יִתְבַּיֵּשׁ מִפְּנֵי בְּנֵי אָדָם הַמַּלְעִיגִים עָלָיו בַּעֲבוֹדַת ה', גַּם בְּהַצְנֵעַ לֶכֶת וּבְשָׁכְבוֹ עַל מִשְׁכָּבוֹ יֵדַע לִפְנֵי מִי הוּא שׁוֹכֵב, וּמִיָּד שֶׁיֵּעוֹר מִשְּׁנָתוֹ יָקוּם בִּזְרִיזוּת לַעֲבוֹדַת בּוֹרְאוֹ יִתְבָּרַךְ וְיִתְעַלֶּה.",
          remaEn: "At the very least, one should not delay past the time when the community prays. “I have set the Lord before me always” is a great principle of the Torah and a high quality of the righteous who walk before God. A person’s sitting, movement, and business when he is alone at home are not as they are before a great king. His speech, loose as he wishes among his household and his relatives, is not his speech in a king’s presence. All the more so when he sets it on his heart that the great King, the Holy One, blessed be He, the whole earth filled with His glory, stands over him and sees his deeds — as it is said, “If a person hides in hidden places, shall I not see him, says the Lord” — then fear and humility before the Lord come upon him at once, and a steady shame before Him. He should not be ashamed before people who mock his service of the Lord. In private, too, and when he lies on his bed, he should know before Whom he lies. As soon as he wakes he should rise with alacrity to the service of his Creator.",
          note: "The lion is the image of Avot 5:20, “be bold as a lion.” The Rema’s longer gloss points to Tehillim 16:8, Yirmiyahu 23:24, and the Guide for the Perplexed III:52, and to the Tur for the close."
        },
        {
          n: 2,
          mechaberHe: "הַמַּשְׁכִּים לְהִתְחַנֵּן לִפְנֵי בוֹרְאוֹ יְכַוֵּין לַשָּׁעוֹת שֶׁמִּשְׁתַּנּוֹת הַמִּשְׁמָרוֹת, שֶׁהֵן בִּשְׁלִישׁ הַלַּיְלָה, וּבְסוֹף שְׁנֵי שְׁלִישֵׁי הַלַּיְלָה, וּבְסוֹף הַלַּיְלָה, שֶׁהַתְּפִלָּה שֶׁיִּתְפַּלֵּל בְּאוֹתָן הַשָּׁעוֹת עַל הַחֻרְבָּן וְעַל הַגָּלוּת רְצוּיָה.",
          mechaberEn: "One who rises early to plead before his Creator should aim for the hours when the watches change — a third of the way through the night, at the end of two thirds, and at the night’s end — for prayer offered then, over the destruction and the exile, is desired.",
          note: "A practice of petition, not the fixed morning service."
        },
        {
          n: 3,
          mechaberHe: "רָאוּי לְכָל יְרֵא שָׁמַיִם שֶׁיְּהֵא מֵצֵר וְדוֹאֵג עַל חֻרְבַּן בֵּית הַמִּקְדָּשׁ.",
          mechaberEn: "It is fitting for everyone who fears Heaven to feel distress and concern over the destruction of the Temple."
        },
        {
          n: 4,
          mechaberHe: "טוֹב מְעַט תַּחֲנוּנִים בְּכַוָּנָה מֵהַרְבּוֹת בְּלֹא כַוָּנָה.",
          mechaberEn: "A few supplications with concentration are better than many without concentration."
        },
        {
          n: 5,
          mechaberHe: "טוֹב לוֹמַר פָּרָשַׁת הָעֲקֵדָה וּפָרָשַׁת הַמָּן וַעֲשֶׂרֶת הַדִּבְּרוֹת וּפָרָשַׁת עוֹלָה וּמִנְחָה וּשְׁלָמִים וְחַטָּאת וְאָשָׁם.",
          mechaberEn: "It is good to recite the passage of the Binding of Isaac, the passage of the manna, the Ten Words, and the passages of the burnt-offering, the meal-offering, the peace-offering, the sin-offering, and the guilt-offering.",
          remaHe: "וְדַוְקָא בְּיָחִיד מֻתָּר לוֹמַר עֲשֶׂרֶת הַדִּבְּרוֹת בְּכָל יוֹם, אֲבָל אָסוּר לְאָמְרָם בְּצִבּוּר.",
          remaEn: "Only an individual may recite the Ten Words every day. To recite them with the congregation is forbidden.",
          note: "The Rema marks the responsa of the Rashba. The concern is that a daily public reading would be mistaken for the whole of the Torah."
        },
        {
          n: 6,
          mechaberHe: "פָּרָשִׁיּוֹת הַקָּרְבָּנוֹת לֹא יֹאמַר אֶלָּא בַּיּוֹם.",
          mechaberEn: "The passages of the offerings should be recited only by day."
        },
        {
          n: 7,
          mechaberHe: "כְּשֶׁיְּסַיֵּם פָּרָשַׁת הָעוֹלָה יֹאמַר: יְהִי רָצוֹן מִלְּפָנֶיךָ שֶׁיְּהֵא זֶה חָשׁוּב וּמְקֻבָּל כְּאִלּוּ הִקְרַבְתִּי עוֹלָה. וְכֵן יֹאמַר אַחַר פָּרָשַׁת הַמִּנְחָה וְהַשְּׁלָמִים, מִפְּנֵי שֶׁהֵן בָּאִים בִּנְדָבָה.",
          mechaberEn: "When he finishes the passage of the burnt-offering he should say: May it be Your will that this be counted and received as if I had offered a burnt-offering. He should say the same after the meal-offering and the peace-offering, because those can be brought as a free-will gift."
        },
        {
          n: 8,
          mechaberHe: "יֹאמַר עִם הַקָּרְבָּנוֹת פָּסוּק: וְשָׁחַט אֹתוֹ עַל יֶרֶךְ הַמִּזְבֵּחַ צָפֹנָה לִפְנֵי ה'.",
          mechaberEn: "With the offerings he should recite the verse, “And he shall slaughter it on the side of the altar, to the north, before the Lord.”"
        },
        {
          n: 9,
          mechaberHe: "יֵשׁ נוֹהֲגִין לוֹמַר פָּרָשַׁת הַכִּיּוֹר, וְאַחַר כָּךְ פָּרָשַׁת תְּרוּמַת הַדֶּשֶׁן, וְאַחַר כָּךְ פָּרָשַׁת הַתָּמִיד, וְאַחַר כָּךְ פָּרָשַׁת מִזְבֵּחַ מַקְטִר קְטֹרֶת וּפָרָשַׁת סַמְמָנֵי הַקְּטֹרֶת וַעֲשִׂיָּיתוֹ.",
          mechaberEn: "Some have the custom to recite the passage of the basin, then the passage of lifting off the ashes, then the daily offering, then the passage of the incense altar and the passage of the incense spices and how it is made."
        }
      ]
    }
  }
};

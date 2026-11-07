/* Layer 2 — technical/runtime settings only. No Torah prose. See data/site.json for approved site copy. */
window.DIBURIM_CONFIG = {
  siteUrl: "https://diburim.org",
  /** Live reader (GitHub Pages or custom domain) for the separate Shulchan Aruch repo */
  externalShulchanAruchUrl: "https://bennyg83.github.io/shulchan_aruch/",
  externalShulchanAruchLabel: "Open translation",
  shulchanAruchRepoUrl: "https://github.com/bennyg83/shulchan_aruch",
  shulchanAruchRepoLabel: "GitHub repository",
  subscribeEndpoint: "",
  contactEmail: "",
  videoSections: [
    {
      id: "kids",
      heading: "Kids",
      videos: [
        {
          id: "rosh-hashana-5787",
          occasion: "Rosh Hashana",
          youtubeId: "92_7WMIU7P8"
        }
      ]
    },
    {
      id: "parsha",
      heading: "Parsha",
      videos: [
        { id: "chayei-sara", parsha: "Chayei Sara", title: "Chayei Sara for children", youtubeId: "" },
        { id: "toldot", parsha: "Toldot", title: "Toldot for children", youtubeId: "" },
        { id: "vayera", parsha: "Vayera", title: "Vayera for children", youtubeId: "" }
      ]
    }
  ]
};

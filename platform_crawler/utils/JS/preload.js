//https://intoli.com/blog/not-possible-to-block-chrome-headless/
//https://github.com/paulirish/headless-cat-n-mouse
Object.defineProperty(navigator, 'webdriver', {
    get: function() {
        return false;
    }
});

const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
    Promise.resolve({ state: Notification.permission }) :
    originalQuery(parameters)
);

// overwrite the `languages` property to use a custom getter
Object.defineProperty(navigator, "languages", {
    get: function() {
      return ["zh-CN", "zh"];
    }
});
Object.defineProperty(navigator, "language", {
    get: function() {
      return "zh-CN";
    }
});

//重写screen 宽高
// Object.defineProperty(screen, "availWidth", {
//     get: function() {
//       return 1920;
//     }
// });
// Object.defineProperty(screen, "availHeight", {
//     get: function() {
//       return 1040;
//     }
// });
// Object.defineProperty(screen, "width", {
//     get: function() {
//       return 1920;
//     }
// });
// Object.defineProperty(screen, "height", {
//     get: function() {
//       return 1080;
//     }
// });

//重写plugin
Object.defineProperty(navigator, "plugins", {
    get: function() {
        return {
            0: {
                0: {
                    description: "Portable Document Format",
                    enabledPlugin: {},
                    suffixes: "pdf",
                    type: "application/x-google-chrome-pdf"
                },
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin",
                "application/x-google-chrome-pdf": {
                    description: "Portable Document Format",
                    enabledPlugin: {},
                    suffixes: "pdf",
                    type: "application/x-google-chrome-pdf"
                }
            },
            1: {
                0: {
                    description: "",
                    enabledPlugin: {},
                    suffixes: "pdf",
                    type: "application/pdf"
                },
                description: "",
                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                length: 1,
                name: "Chrome PDF Viewer",
                "application/pdf": {
                    description: "",
                    enabledPlugin: {},
                    suffixes: "pdf",
                    type: "application/pdf"
                }
            },
            2: {
                0: {
                    description: "Native Client Executable",
                    enabledPlugin: {},
                    suffixes: "",
                    type: "application/x-nacl"
                },
                1: {
                    description: "Portable Native Client Executable",
                    enabledPlugin: {},
                    suffixes: "",
                    type: "application/x-pnacl"
                },
                description: "",
                filename: "internal-nacl-plugin",
                length: 2,
                name: "Native Client",
                "application/x-nacl": {
                    description: "Native Client Executable",
                    enabledPlugin: {},
                    suffixes: "",
                    type: "application/x-nacl"
                },
                "application/x-pnacl": {
                    description: "Portable Native Client Executable",
                    enabledPlugin: {},
                    suffixes: "",
                    type: "application/x-pnacl"
                }
            },
            3: {
                0: {
                    description: "Shockwave Flash",
                    enabledPlugin: {},
                    suffixes: "swf",
                    type: "application/x-shockwave-flash"
                },
                1: {
                    description: "Shockwave Flash",
                    enabledPlugin: {},
                    suffixes: "spl",
                    type: "application/futuresplash"
                },
                description: "Shockwave Flash 29.0 r0",
                filename: "pepflashplayer.dll",
                length: 2,
                name: "Shockwave Flash",
                "application/futuresplash": {
                    description: "Shockwave Flash",
                    enabledPlugin: {},
                    suffixes: "spl",
                    type: "application/futuresplash"
                },
                "application/x-shockwave-flash": {
                    description: "Shockwave Flash",
                    enabledPlugin: {},
                    suffixes: "swf",
                    type: "application/x-shockwave-flash"
                }
            },
            4: {
                0: {
                    description: "Widevine Content Decryption Module",
                    enabledPlugin: {},
                    suffixes: "",
                    type: "application/x-ppapi-widevine-cdm"
                },
                description: "Enables Widevine licenses for playback of HTML audio/video content. (version: 1.4.9.1070)",
                filename: "widevinecdmadapter.dll",
                length: 1,
                name: "Widevine Content Decryption Module",
                "application/x-ppapi-widevine-cdm": {
                    description: "Widevine Content Decryption Module",
                    enabledPlugin: {},
                    suffixes: "",
                    type: "application/x-ppapi-widevine-cdm"
                }
            },
            length: 5,
            'Chrome PDF Plugin': {
                0: {
                    description: "Portable Document Format",
                    enabledPlugin: {},
                    suffixes: "pdf",
                    type: "application/x-google-chrome-pdf"
                },
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin",
                "application/x-google-chrome-pdf": {
                    description: "Portable Document Format",
                    enabledPlugin: {},
                    suffixes: "pdf",
                    type: "application/x-google-chrome-pdf"
                }
            },
            'Chrome PDF Viewer': {
                0: {
                    description: "",
                    enabledPlugin: {},
                    suffixes: "pdf",
                    type: "application/pdf"
                },
                description: "",
                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                length: 1,
                name: "Chrome PDF Viewer",
                "application/pdf": {
                    description: "",
                    enabledPlugin: {},
                    suffixes: "pdf",
                    type: "application/pdf"
                }
            },
            'Native Client': {
                0: {
                    description: "Native Client Executable",
                    enabledPlugin: {},
                    suffixes: "",
                    type: "application/x-nacl"
                },
                1: {
                    description: "Portable Native Client Executable",
                    enabledPlugin: {},
                    suffixes: "",
                    type: "application/x-pnacl"
                },
                description: "",
                filename: "internal-nacl-plugin",
                length: 2,
                name: "Native Client",
                "application/x-nacl": {
                    description: "Native Client Executable",
                    enabledPlugin: {},
                    suffixes: "",
                    type: "application/x-nacl"
                },
                "application/x-pnacl": {
                    description: "Portable Native Client Executable",
                    enabledPlugin: {},
                    suffixes: "",
                    type: "application/x-pnacl"
                }
            },
            'Shockwave Flash': {
                0: {
                    description: "Shockwave Flash",
                    enabledPlugin: {},
                    suffixes: "swf",
                    type: "application/x-shockwave-flash"
                },
                1: {
                    description: "Shockwave Flash",
                    enabledPlugin: {},
                    suffixes: "spl",
                    type: "application/futuresplash"
                },
                description: "Shockwave Flash 29.0 r0",
                filename: "pepflashplayer.dll",
                length: 2,
                name: "Shockwave Flash",
                "application/futuresplash": {
                    description: "Shockwave Flash",
                    enabledPlugin: {},
                    suffixes: "spl",
                    type: "application/futuresplash"
                },
                "application/x-shockwave-flash": {
                    description: "Shockwave Flash",
                    enabledPlugin: {},
                    suffixes: "swf",
                    type: "application/x-shockwave-flash"
                }
            },
            'Widevine Content Decryption Module': {
                0: {
                    description: "Widevine Content Decryption Module",
                    enabledPlugin: {},
                    suffixes: "",
                    type: "application/x-ppapi-widevine-cdm"
                },
                description: "Enables Widevine licenses for playback of HTML audio/video content. (version: 1.4.9.1070)",
                filename: "widevinecdmadapter.dll",
                length: 1,
                name: "Widevine Content Decryption Module",
                "application/x-ppapi-widevine-cdm": {
                    description: "Widevine Content Decryption Module",
                    enabledPlugin: {},
                    suffixes: "",
                    type: "application/x-ppapi-widevine-cdm"
                }
            }
        };
    }
});

//重写window.chrome
window.navigator.chrome = {
    app: {
        isInstalled: false,
        getIsInstalled: function(){ return false; }   
    },
    webstore: {
        install: function(url, onSuccess, onFailure) {},
        onDownloadProgress: {},
        onInstallStageChanged: {}
    },
    csi: function(){
        return {
            onloadT: 1531198168690,
            pageT: 9845078.779,
            startE: 1531198164528,
            tran: 15
        }
    },
    loadTimes: function(){
        return {"requestTime":1531198164.528,"startLoadTime":1531198164.528,"commitLoadTime":1531198165.871,"finishDocumentLoadTime":1531198168.69,"finishLoadTime":1531198171.872,"firstPaintTime":1531198166.734,"firstPaintAfterLoadTime":0,"navigationType":"Other","wasFetchedViaSpdy":false,"wasNpnNegotiated":true,"npnNegotiatedProtocol":"http/1.1","wasAlternateProtocolAvailable":false,"connectionInfo":"http/1.1"}
    },
    runtime: {
        "PlatformOs":{"MAC":"mac","WIN":"win","ANDROID":"android","CROS":"cros","LINUX":"linux","OPENBSD":"openbsd"},
        "PlatformArch":{"ARM":"arm","X86_32":"x86-32","X86_64":"x86-64"},"PlatformNaclArch":{"ARM":"arm","X86_32":"x86-32","X86_64":"x86-64"},"RequestUpdateCheckStatus":{"THROTTLED":"throttled","NO_UPDATE":"no_update","UPDATE_AVAILABLE":"update_available"},"OnInstalledReason":{"INSTALL":"install","UPDATE":"update","CHROME_UPDATE":"chrome_update","SHARED_MODULE_UPDATE":"shared_module_update"},"OnRestartRequiredReason":{"APP_UPDATE":"app_update","OS_UPDATE":"os_update","PERIODIC":"periodic"},
        connect: function(){},
        sendMessage: function(){}
    }
};

// Pass toString test, though it breaks console.debug() from working
// window.console.debug = () => {
//     return null;
// };


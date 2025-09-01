export default {
  expo: {
    name: "OkemID",
    slug: "okemid",
    scheme: "okemid",
    sdkVersion: "53.0.0",
    icon: "./assets/icon.png",
    splash: {
      image: "./assets/splash.png",
      resizeMode: "contain",
      backgroundColor: "#ffffff",
    },
    android: {
      adaptiveIcon: {
        foregroundImage: "./assets/adaptive-icon.png",
        backgroundColor: "#ffffff",
      },
    },
    extra: {
      eas: {
        projectId: "fill-later",
      },
    },
    experiments: {
      reactNative: {
        disableBridgeless: true,
      },
    },
  },
};

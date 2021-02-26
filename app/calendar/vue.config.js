module.exports = {
    publicPath: "./",
    css: {
        extract: false,
    },
    configureWebpack: {
        externals: {
            vue: "Vue",
            axios: "axios",
            "element-ui": "ELEMENT",
        }
    },
}
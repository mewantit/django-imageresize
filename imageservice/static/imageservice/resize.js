// Functions for appending size information on a URL
resize = function(url, width, height) {
    var filenameStart = Math.max(url.lastIndexOf("/"), 0);
    var path = url.substring(0, filenameStart);
    var filename = url.substring(filenameStart);
    var extensionStart = filename.lastIndexOf(".");
    if (extensionStart == -1) {
        extensionStart = filename.length;
    }
    var extension = filename.substring(extensionStart);
    var filenameWithoutExtension = filename.substring(0, extensionStart);
    return path + filenameWithoutExtension + "." + width.toString() + 
           "x" + height.toString() + extension;
}
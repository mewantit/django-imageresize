// Functions for appending size information on a URL
resize = function(url, width, height) {
    return template( url, width.toString() + "x" + height.toString() );
}

_getFile = function(url) {
	var filenameStart = Math.max(url.lastIndexOf("/"), 0);
    var path = url.substring(0, filenameStart);
    var filename = url.substring(filenameStart);
    var extensionStart = filename.lastIndexOf(".");
    if (extensionStart == -1) {
        extensionStart = filename.length;
    }
    var extension = filename.substring(extensionStart);
    var nameWithoutExt = filename.substring(0, extensionStart);

    return new File(path, nameWithoutExt, extension);
}

File = function(path, name, extension) {
	this.path = path;
	this.name = name;
	this.extension = extension || "";
}

template = function(url, templateName) {
	var f = _getFile(url);
    return f.path + f.name + "." + templateName + f.extension;
}

YUI.add("type_advance_desktop_viewer", function(c, b) {
    var a = c.Base.create("MyApp", c.Base, [c.Af.Applets, c.Af.Rapid, c.Highlander.Client], {
        initializer: function(e) {
            var f, g = c.config.doc,
                i, d = "ontouchstart" in g.documentElement,
                h = function(j) {
                    return ["INPUT", "TEXTAREA"].indexOf(j.nodeName) !== -1;
                };
            for (i in c.My.Extensions) {
                if (c.Lang.isFunction(c.My.Extensions[i].init)) {
                    c.My.Extensions[i].NAME = i;
                    c.later(Math.floor(Math.random() * 20), c.My.Extensions[i], function() {
                        this.init();
                    });
                }
            }
            f = c.one(".Col2");
            c.on("orientationchange", function(j) {
                if (f) {
                    f.setStyle("display", "none");
                    c.later(0, this, function() {
                        f.setStyle("display", "block");
                    }, false);
                }
            }, window);
            if (d) {
                c.on("touchstart", function(k) {
                    var j = k.target;
                    if (!h(j) && h(g.activeElement) && !j.ancestor(".yui3-aclist", true)) {
                        g.activeElement.blur();
                    }
                });
            }
        }
    }, {});
    c.namespace("My").App = a;
}, "0.0.1", {
    requires: ["stencil", "af-applets", "base", "af-rapid", "af-beacon", "highlander-client"]
}); /* Copyright (c) 2017, Yahoo! Inc.  All rights reserved. */
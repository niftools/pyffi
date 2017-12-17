// Window Scroll
var windowScroll = function() {
    $(window).scroll(function() {
        var scrollPos = $(this).scrollTop();
        var system = {
            win: false,
            mac: false,
            xll: false
        };

        var p = navigator.platform;
        system.win = p.indexOf("Win") == 0;
        system.mac = p.indexOf("Mac") == 0;
        system.xll = (p == "X11") || (p.indexOf("Linux") == 0);

        if (system.win || system.mac || system.xll) {
            if ($(window).scrollTop() > 70) {
                $('.site-header').addClass('site-header-nav-scrolled');
                $('nav:not(.navbar-inversed):not(#toc)').addClass('navbar-inverse');
            } else {
                $('.site-header').removeClass('site-header-nav-scrolled');
                $('nav:not(.navbar-inversed):not(#toc)').removeClass('navbar-inverse');
            }
        } else {
            if ($(window).scrollTop() > 40) {
                $('.site-header').addClass('site-header-nav-scrolled-ph');
                $('nav:not(.navbar-inversed):not(#toc)').addClass('navbar-inverse');
            } else {
                $('.site-header').removeClass('site-header-nav-scrolled-ph');
                $('nav:not(.navbar-inversed):not(#toc)').removeClass('navbar-inverse');
            }
        }
    });
};

$(document).ready(function() {
    windowScroll();

    //$('#toc').affix('checkPosition');

    //setTimeout(function() {
    $('[data-spy="scroll"]').each(function() {
        var $spy = $(this).scrollspy('refresh')
    });
    //}, 400);
});

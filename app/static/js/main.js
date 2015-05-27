'use strict';

var fufu = (function () {

  var docEl,
  hamburger,
  navMain,
  close,
  back,
  menu,
  showSignin,
  showRegister,
  showSearch,
  signin,
  register,
  search,
  logo,
  navClose,
  classes;

  docEl = document.documentElement;
  hamburger = document.getElementById("jump");
  close = document.getElementById("close");
  back = document.getElementById("back");
  menu = document.getElementById("menu");
  showSignin = document.getElementById("show-signin");
  showRegister = document.getElementById("show-register");
  showSearch = document.getElementById("show-search");
  signin = document.getElementById("signin");
  register = document.getElementById("register");
  search = document.getElementById("search");
  logo = document.getElementById("logo");
  navClose = document.getElementById("nav-close");

  if(hamburger) {
    navMain = hamburger.parentNode;
  }

  function getTarget(evt) {
    evt = evt || window.event;
    return evt.target || evt.srcElement;
  }

  function trim(str) {
    return str.trim ? str.trim() : str.replace(/^\s+|\s+$/g,'');
  }

  function hasClass(el, cn) {
    return (' ' + el.className + ' ').indexOf(' ' + cn + ' ') !== -1;
  }

  function addClass(el, cn) {
    if (cn.indexOf(' ') >= 0) {
      classes = cn.split(' ');
      for (var p = 0; p < classes.length; p++) {
        if(!hasClass(el, classes[p])) {
          el.className = (el.className === '') ? classes[p] : el.className + ' ' + classes[p];
        }
      }
    } else {
      if (!hasClass(el, cn)) {
        el.className = (el.className === '') ? cn : el.className + ' ' + cn;
      }
    }
  }

  function removeClass(el, cn) {
    if (cn.indexOf(' ') >= 0) {
      classes = cn.split(' ');
      for (var p = 0; p < classes.length; p++) {
        el.className = trim((' ' + el.className + ' ').replace(' ' + classes[p] + ' ', ' '));
      }
    } else {
      el.className = trim((' ' + el.className + ' ').replace(' ' + cn + ' ', ' '));
    }
  }

  function toggleClass(el, cn) {
    if(hasClass(el, cn)) {
      removeClass(el, cn);
    } else {
      addClass(el, cn);
    }
  }

  function bindEvent(target, type, listener, capture) {
    if(window.addEventListener) {
      target.addEventListener(type, listener, capture);
    } else if(window.attachEvent && typeof window.event !== 'undefined') {
      if(type === 'blur') {
        type = 'focusout';
      } else if(type === 'focus') {
        type = 'focusin';
      }
      target.attachEvent( 'on' + type, listener );
    }
  }

  function preventActions(ev) {
    ev = ev || window.event;
    if(ev.stopPropagation && ev.preventDefault) {
      ev.stopPropagation();
      ev.preventDefault();
    } else {
      ev.cancelBubble = true;
      ev.returnValue = false;
    }
  }

  function hideBackButton() {
    addClass(back, "hidden");
  }

  function hideSignInMenu() {
    addClass(signin, "hidden");
  }

  function hideRegisterMenu() {
    addClass(register, "hidden");
  }

  function hideSearchMenu() {
    addClass(search, "hidden");
  }

  function hideFormMenus() {
    if(back) {
      hideBackButton();
    }
    if (signin) {
      hideSignInMenu();
    }
    if (register) {
      hideRegisterMenu();
    }
    if (search) {
      hideSearchMenu();
    }
  }

  function hideMenu() {
    removeClass(hamburger, "hidden");
    addClass(close, "hidden");
    addClass(menu, "hidden");
    addClass(navClose, "hidden");
    removeClass(navMain, "nav-main-active");
  }

  function showMenu() {
    addClass(hamburger, "hidden");
    removeClass(close, "hidden");
    removeClass(menu, "hidden");
    removeClass(navClose, "hidden");
    addClass(navMain, "nav-main-active");
  }

  function hideNonFormMenu() {
    addClass(close, "hidden");
    addClass(logo, "hidden");
  }

  function showNonFormMenu() {
    removeClass(close, "hidden");
    removeClass(logo, "hidden");
  }

  return {
    docEl: docEl,
    hamburger: hamburger,
    close: close,
    back: back,
    menu: menu,
    showSignin: showSignin,
    showRegister: showRegister,
    showSearch: showSearch,
    signin: signin,
    register: register,
    search: search,
    logo: logo,
    navClose: navClose,
    addClass: addClass,
    removeClass: removeClass,
    toggleClass: toggleClass,
    bindEvent: bindEvent,
    preventActions: preventActions,
    hideFormMenus: hideFormMenus,
    hideBackButton: hideBackButton,
    hideSignInMenu: hideSignInMenu,
    hideRegisterMenu: hideRegisterMenu,
    hideSearchMenu: hideSearchMenu,
    hideMenu: hideMenu,
    showMenu: showMenu,
    hideNonFormMenu: hideNonFormMenu,
    showNonFormMenu: showNonFormMenu
  };

})();

(function (window, document) {

  if(fufu.menu) {

    fufu.removeClass(fufu.docEl,"no-js");
    fufu.addClass(fufu.docEl,"js");
    fufu.hideMenu();
    fufu.hideFormMenus();

    // burger nav

    fufu.bindEvent(fufu.hamburger, "click", function (ev) {
      fufu.preventActions(ev);
      fufu.showMenu();
    });

    fufu.bindEvent(fufu.close, "click", function (ev) {
      fufu.preventActions(ev);
      fufu.hideMenu();
    });

    fufu.bindEvent(fufu.navClose, "click", function (ev) {
      fufu.preventActions(ev);
      fufu.hideMenu();
      // hide menu forms too
      fufu.hideFormMenus();
      fufu.removeClass(fufu.logo, "hidden");
    });

    fufu.bindEvent(fufu.back, "click", function (ev) {
      fufu.preventActions(ev);
      fufu.showNonFormMenu();
      fufu.showMenu();
      fufu.hideFormMenus();
    });
  }

  // menu forms

  if(fufu.menu && fufu.signin && fufu.showSignin) {

    fufu.bindEvent(fufu.showSignin, "click", function (ev) {
      fufu.preventActions(ev);
      fufu.hideNonFormMenu();
      fufu.addClass(fufu.menu, "hidden");
      fufu.removeClass(fufu.back, "hidden");
      fufu.removeClass(fufu.signin, "hidden");
    });

  }

  if(fufu.menu && fufu.register && fufu.showRegister) {

    fufu.bindEvent(fufu.showRegister, "click", function (ev) {
      fufu.preventActions(ev);
      fufu.hideNonFormMenu();
      fufu.addClass(fufu.menu, "hidden");
      fufu.removeClass(fufu.back, "hidden");
      fufu.removeClass(fufu.register, "hidden");
    });

  }

  if(fufu.menu && fufu.search) {

    fufu.bindEvent(fufu.showSearch, "click", function (ev) {
      fufu.preventActions(ev);
      fufu.hideNonFormMenu();
      fufu.addClass(fufu.menu, "hidden");
      fufu.removeClass(fufu.back, "hidden");
      fufu.removeClass(fufu.search, "hidden");
    });

  }


}(window, window.document));

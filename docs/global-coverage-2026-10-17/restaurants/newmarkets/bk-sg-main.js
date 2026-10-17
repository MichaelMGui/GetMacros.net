// A '$' sign to define/access jQuery
var $ = jQuery.noConflict(); // '()' to be performed on the element(s)
BK = function () {
    var _mqMobile = window.matchMedia('screen and (max-width: 767px)'),
        _mqTablet = window.matchMedia('screen and (max-width: 1199px)'),
        _mqDesktop = window.matchMedia('screen and (min-width: 1200px)');
    return {
        init: function () {
            BK.initTracking();
            BK.nav.init();
            BK.popLocation();
            BK.productDetail.init();
            BK.mymeal.init();
            BK.initAppBanners();
            BK.initAlertSignupPopup();
            if ($('body').hasClass('home')) {
                BK.home.init();
            }
            if ($('#locationsMap').length) {
                BK.locations.init();
            }
            if ($('.food-item-block').length) {
                BK.menu.init();
            }
            if ($('body').hasClass('other')) {
                BK.other.init();
            }
            if ($('.MadeToOrder-slider').length) {
                BK.initMadeToOrderSlider();
            }
            if ($('.OurStory-slider').length) {
                BK.initOurStorySlider();
            }
        },
        getMq: function (mq) {
            switch (mq) {
                case 'mobile':
                    return _mqMobile;
                    break;
                case 'tablet':
                    return _mqTablet;
                    break;
                case 'desktop':
                    return _mqDesktop;
                    break;
                default:
                    return null;
            }
        },
        initTracking: function () {
            $('body').on('click', '[data-ga]', function (e) {
                var args = $(this).data('ga').split(',');
                var outboundUrl = $(this).data('gaOutboundUrl');
                if (args.length) {
                    if (outboundUrl) {
                        e.preventDefault();
                        BK.analytics.track(args, function () {
                            window.location = outboundUrl;
                        });
                    } else {
                        BK.analytics.track(args);
                    }
                }
            });
        },
        initAlertSignupPopup: function () {
            var mqDesktopMatch = BK.getMq('desktop').matches;
            if (mqDesktopMatch) {
                var timerFirstClick;
                var timerSecondClick;
                $("li.alert-signup-popup a#btnLetter").on('click', function () {
                    var cl = $(this).attr('class');
                    if (cl == 'active') {
                        $(this).removeClass('active');
                        $(this).next().removeClass('active');
                        $("li.alert-signup-popup .popup").fadeOut(200);
                        if (timerSecondClick)
                            window.clearTimeout(timerSecondClick);
                    } else {
                        $(this).addClass('active');
                        $(this).next().addClass('active');
                        $("li.alert-signup-popup .popup").fadeIn(200);
                    }
                });
                $("li.alert-signup-popup .popup a#lnkClose").on('click', function () {
                    $("li.alert-signup-popup a#btnLetter").click();
                });
                var firstTimeSeePopup = ($.cookie('bk_seenAlertSignupPopup') == null);
                if (firstTimeSeePopup) {
                    $.cookie('bk_seenAlertSignupPopup', 'true', {
                        expires: 30,
                        path: '/'
                    });
                    timerFirstClick = setTimeout(function () {
                        $("li.alert-signup-popup a#btnLetter").click();
                    }, 2000);
                    timerSecondClick = setTimeout(function () {
                        $("li.alert-signup-popup a#btnLetter").click();
                    }, 7000);
                }
            }
        },
        initAppBanners: function () {
            //$.smartbanner({
            //    title: 'BURGER KING® App',
            //    author: 'BURGER KING',
            //    layer: true,
            //    button: 'INSTALL',
            //    icon: 'http://a3.mzstatic.com/us/r30/Purple1/v4/b1/d9/7c/b1d97cfe-5eb0-75da-6b01-5b62a978eae9/icon175x175.jpeg',
            //    googlePlayDirectURL: 'https://play.google.com/store/apps/details?id=com.emn8.mobilem8.nativeapp.bk&referrer=utm_fiksu_adid%3D1010877',
            //    appStoreDirectURL: 'https://handler.fiksu.com/click?adid=12cec5e0-4e3c-0132-3e5d-22000b058c63&adnet=XVT7PFS3&appid=638323895&b=10l3Ik&device_class=ios&s=00001'
            //});
        },
        initMadeToOrderSlider: function () {
            var madeToOrderSlider = $('.MadeToOrder-slider .owl-carousel');
            madeToOrderSlider.on('initialized.owl.carousel', function (event) {
                var mqMobileMatch = BK.getMq('mobile').matches;
                if (mqMobileMatch) {
                    BK.adjustMadeToOrderArrows();
                }
            });
            madeToOrderSlider.owlCarousel({
                loop: true,
                nav: true,
                dots: false,
                center: true,
                navText: ['<div class="hover"></div><div class="arrow"></div>', '<div class="hover"></div><div class="arrow"></div>'],
                responsiveClass: true,
                responsive: {
                    0: {
                        margin: 0,
                        autoWidth: false,
                        items: 1
                    },
                    768: {
                        margin: -75,
                        autoWidth: true
                    }
                }
            });
        },
        adjustMadeToOrderArrows: function () {
            var madeToOrderSlider = $('.MadeToOrder-slider .owl-carousel');
            var itemH = $($('.owl-item .item', madeToOrderSlider)[0]).height();
            var imageH = $('.owl-item.center .item img', madeToOrderSlider).height();
            var bottom = (itemH - imageH) + (imageH / 2) * 0.8;
            $('.owl-controls .owl-nav .owl-prev .arrow', madeToOrderSlider).css('bottom', bottom + 'px');
            $('.owl-controls .owl-nav .owl-next .arrow', madeToOrderSlider).css('bottom', bottom + 'px');
        },
        adjustOurStoryArrows: function () {
            var ourStorySlider = $('.OurStory-slider .owl-carousel');
            var itemH = $($('.owl-item .item', ourStorySlider)[0]).height();
            var imageH = $('.owl-item.center .item img', ourStorySlider).height();
            var bottom = itemH - imageH - 42;
            $('.owl-controls .owl-nav .owl-prev .arrow', ourStorySlider).css('bottom', bottom + 'px');
            $('.owl-controls .owl-nav .owl-next .arrow', ourStorySlider).css('bottom', bottom + 'px');
        },
        initOurStorySlider: function () {
            var ourStorySlider = $('.OurStory-slider .owl-carousel');
            ourStorySlider.on('initialized.owl.carousel', function (event) {
                var mqMobileMatch = BK.getMq('mobile').matches;
                if (mqMobileMatch) {
                    BK.adjustOurStoryArrows();
                }
            });
            ourStorySlider.on('resized.owl.carousel', function (event) {
                var mqMobileMatch = BK.getMq('mobile').matches;
                if (mqMobileMatch) {
                    BK.adjustOurStoryArrows();
                } else {
                    $('.owl-controls .owl-nav .owl-prev .arrow', ourStorySlider).css('bottom', '');
                    $('.owl-controls .owl-nav .owl-next .arrow', ourStorySlider).css('bottom', '');
                }
            });
            ourStorySlider.owlCarousel({
                loop: true,
                nav: true,
                dots: false,
                center: true,
                navText: ['<div class="hover"></div><div class="arrow"></div>', '<div class="hover"></div><div class="arrow"></div>'],
                responsiveClass: true,
                responsive: {
                    0: {
                        margin: 0,
                        autoWidth: false,
                        items: 1
                    },
                    768: {
                        margin: 10,
                        autoWidth: true
                    }
                }
            });
        },
        popLocation: function () {
            if ($.cookie('bkMyLocation')) {
                var locationCookie = $.cookie('bkMyLocation'),
                    todayString = (new Date).toString().substr(0, 3);
                var text = '<a href="' + base_url + 'Locator/Index"><i class="icon icon_pindrop-orange"></i>Your BK - ' + locationCookie.address1 + ' - ';
                if (todayString === 'Fri' || todayString === 'Sat')
                    text += todayString + ' ' + locationCookie.weekendStoreHours;
                else
                    text += todayString + ' ' + locationCookie.weekdayStoreHours;
                text += '</a>';
                $('.utility-header li.location').html(text);
            }
        },
        templates: {
            'mymeal-modal': '<div class="modal fade" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><a href="#" class="close" data-dismiss="modal" aria-hidden="true"><i class="icon icon_close-gray"></i></a><h4 class="modal-title" id="myModalLabel">My Meal</h4></div><div class="modal-body"><span>Click on an item to customize with premium ingredients.</span>{{{items}}}{{{nutrition}}}</div><div class="modal-footer"><a href="#" class="bk-btn bk-btn-lightBrown btn-default bk-btn-email" data-dismiss="modal" data-ga="send,event,myMealModal,click,emailShare">Send By Email<i class="icon icon_email-white"></i></a><a href="#" class="bk-btn bk-btn-orange btn-primary bk-btn-print" data-dismiss="modal" data-ga="send,event,myMealModal,click,printMeal">Print<i class="icon icon_print-white"></i></a></div></div></div></div>',
            'mymeal-items': '<table class="items-table"><thead><tr><th colspan="2">Items</th><th>Calories</th></tr></thead><tbody>{{#items}}<tr><td class="action"><a class="delete" data-item-index="{{idx}}"><i class="icon icon_close-gray"></i></a></td><td class="item"><a href="{{url}}{{#params}}{{/params}}" data-ga="send,event,myMealModal,click,customize" data-ga-outbound-url="{{url}}{{#params}}{{/params}}">{{{label}}}</a></td><td class="calories">{{roundedCalories}}</td></tr>{{/items}}{{^items}}<tr><td colspan="2" class="action"><span>No items</span></td><td class="calories">0</td></tr>{{/items}}</tbody><tfoot><tr><td colspan="2" class="label">Total</td><td class="calories">{{totalCalories}}</td></tr></tfoot></table>',
            'mymeal-nutrition': '<div class="nutrition-content"{{^isVisible}} style="display: none;"{{/isVisible}}>{{#nutrition}}<div class="nutrition-data">{{#isMyMeal}}<h3>Meal Nutrition</h3>{{/isMyMeal}}<div class="col-sm-4"><ul><li class="calories"><h5 class="label">Calories</h5><p class="value"><span class="number">{{calories}}</span></p></li><li class="protein"><h5 class="label">Protein</h5><p class="value"><span class="number">{{protein}}</span><abbr class="unit">g</abbr></p></li><li class="carbohydrates"><h5 class="label">Carbohydrates</h5><p class="value"><span class="number">{{carbohydrates}}</span><abbr class="unit">g</abbr></p></li></ul></div><div class="col-sm-4"><ul><li class="sugar"><h5 class="label">Sugar</h5><p class="value"><span class="number">{{sugar}}</span><abbr class="unit">g</abbr></p></li><li class="fat"><h5 class="label">Fat</h5><p class="value"><span class="number">{{fat}}</span><abbr class="unit">g</abbr></p></li><li class="saturatedfat"><h5 class="label">Saturated Fat</h5><p class="value"><span class="number">{{saturatedfat}}</span><abbr class="unit">g</abbr></p></li></ul></div><div class="col-sm-4"><ul><li class="transfat"><h5 class="label">Trans Fat</h5><p class="value"><span class="number">{{transfat}}</span><abbr class="unit">g</abbr></p></li><li class="cholesterol"><h5 class="label">Cholesterol</h5><p class="value"><span class="number">{{cholesterol}}</span><abbr class="unit">mg</abbr></p></li><li class="sodium"><h5 class="label">Sodium</h5><p class="value"><span class="number">{{sodium}}</span><abbr class="unit">mg</abbr></p></li></ul></div></div>{{/nutrition}}<p class="allergens">{{#allergens}}<span class="allergens-list"><strong>Allergens:</strong> {{.}}</span>{{/allergens}}{{^isMyMeal}}<span class="full-menu"><a href="/pdfs/nutrition.pdf" target="_blank" data-ga="send,event,nutritionInfo,download,fullMenu"><strong class="bkOrange">Download our Full Menu</strong></a> to view all nutrition information.</span>{{/isMyMeal}}</p>{{^isMyMeal}}<p class="footnote">Not all products shown are available in every restaurant. Price and participation will vary. Note: Certain activities provided via this website may be covered by U.S. Patent 6,585,516</p>{{/isMyMeal}}</div>',
            'product-detail': '<section id="product-dropdown" data-product-id="{{id}}" class="col-xs-12 dropdown"><div class="wrapper"><div class="container-fluid product-hero"><div class="row content clearfix"><a class="close" href="#" data-ga="send,event,product,click,detailsClose"><i class="icon icon_close-gray">Close</i></a><hgroup class="col-sm-6 text-left title-group"><h1 class="title">{{{title}}}</h1><h2 class="subtitle">{{{subtitle}}}</h2></hgroup><div class="row"><div class="image col-xs-12 col-sm-6 text-right"><img src="{{{image}}}" /></div><div class="description col-sm-6 text-left">{{{description}}}<h3>Nutritional Information</h3><table style="width:100%;"><caption style="font-weight:bold;text-align:left;padding-bottom:3px;">Per serving {{size}}</caption><tbody><tr><td>Calories</td><td><span align="center">{{calories}}</span> kcal</td></tr><tr><td>Fat</td><td><span align="center">{{fat}}</span> g</td></tr><tr><td>Saturated Fat</td><td><span align="center">{{saturatedfat}}</span> g</td></tr><tr><td>Sodium</td><td><span align="center">{{sodium}}</span> mg</td></tr><tr><td>Carbohydrates</td><td><span align="center">{{carbohydrates}}</span> g</td></tr><tr><td>Fiber</td><td><span align="center">{{fiber}}</span> g</td></tr><tr><td>Sugar</td><td><span align="center">{{sugar}}</span> g</td></tr><tr><td>Proteins</td><td><span align="center">{{protein}}</span> g</td></tr></tbody></table>{{#allergens}}<p><strong>Allergens:</strong> {{.}}</p>{{/allergens}}</div></div><p style="text-align: justify; font-size: 10px">The information provided by Burger King Singapore regarding our food is current as of October 2025. The nutritional information is derived from the information provided by Burger King’s suppliers. Limited time only (“LTO”) have not been included. The product formulations do change periodically. Product availability and nutritional information for some menu items may vary by location. Variations may occur depending on the supplier and/or product preparation. Burger King do no assume responsibility for a person’s sensitivity or allergy to any food item provided in our restaurants. Please consult your healthcare provider for questions regarding your diet. If you have specific questions about our menu, please contact us via the web at https://www.burgerking.com.sg/Contact/Feedback. The sodium content of French Fries may vary based on the amount added after cooking. The information displayed is for unsalted French Fries. Burger King Singapore makes no claim that the Plant-based WHOPPPER® meets the requirement of a vegan or vegetarian diet. The Plant-based patty is cooked on the same grill as meat patties.</p></div></div></section>',
            'location-address': '<div class="location col-xs-12 col-sm-6{{#isMyLocation}} myLocation{{/isMyLocation}}" data-restaurant-id="{{id}}"><a class="markerArea" target="_blank" href="{{directionsUrl}}">{{#isMyLocation}}<i class="icon icon_pindrop-blue"></i><span class="index myBk">my<br>BK</span>{{/isMyLocation}}{{^isMyLocation}}<i class="icon icon_pindrop-orange"></i><span class="index">{{num}}</span>{{/isMyLocation}}</a><dl class="locationContent"><dt class="mainAddress">{{title}}</dt><dd class="cityStateZip">{{cityStateZip}}</dd><dd class="info"><span class="phone">Phone: {{phoneNumber}} </span></dd><dd class="links">{{#offersDelivery}}<a href="#" class="link makeMyLocation">Make this My BK</a>{{/offersDelivery}}{{#offersDelivery}}<a href="{{deliveryUrl}}">Get Delivery <i class="icon icon_truck-orange"></i></a>{{/offersDelivery}}<a class="link directions" target="_blank" href="{{directionsUrl}}">Directions</a><a class="link more-info" href="{{detailsPageUrl}}">More Info</a><dd class="store-hours">{{{storeHours}}}</dd></dl></div>',
            'flip-card': '<ul id="flick" class="flick">{{#items}}<li class="item"><div class="flipContainer" data-ga="send,event,socialTiles,click,flip"><div class="back"><div class="bgFlip" style="background-image:url({{{imgsrc}}});"></div><div class="content"><div class="header"><i class="icon icon_logo-main"></i>BURGER KING</div><div class="text"><div>{{{description}}}</div></div><div class="actions">{{#isTwitter}}<span class="reply"><a href="https://twitter.com/intent/tweet?in_reply_to={{id}}" target="_blank"><i class="icon icon_reply-brown"></i>Reply</a></span><span class="retweet"><a href="https://twitter.com/intent/retweet?tweet_id={{id}}" target="_blank"><i class="icon icon_retweet-brown"></i>Retweet</a></span><span class="favorite"><a href="https://twitter.com/intent/favorite?tweet_id={{id}}" target="_blank"><i class="icon icon_favorite-clicked-brown"></i>Favorite</a></span>{{/isTwitter}}<span class="like"><a href="{{link}}" target="_blank"><i class="icon icon_like-brown"></i>Like</a></span></div></div></div><div class="front" style="background-image: url({{{imgsrc}}});"></div></div></li>{{/items}}</ul>'
        },
        tempLocation: true,
        util: {
            resultOf: function (object, property) {
                if (object == null) return void 0;
                var value = object[property];
                return $.isFunction(value) ? object[property]() : value;
            },
            getUniqueArray: function (arr) {
                var i = 0,
                    a = [],
                    obj = {};
                do {
                    if (!(arr[i] in obj)) {
                        a.push(arr[i]);
                        obj[arr[i]] = true;
                    }
                } while (arr[++i]);
                return a;
            }
        }
    }
}();
BK = BK || {};
BK.analytics = function () {
    var _timer = 0;
    var hasGA = false;

    function _track(options, callback) {
        if (hasGA) {
            if (callback !== undefined) {
                options.push({
                    hitCallback: function () {
                        window.clearTimeout(_timer);
                        callback();
                    }
                });
            }
            window.ga.apply(window, options);
        } else {
            if (callback !== undefined) callback();
        }
    }
    if (window.ga !== undefined) {
        hasGA = true;
    }
    return {
        track: _track
    }
}();
BK = BK || {};
BK.home = function () {
    var bkFlicker, templates = {};
    return {
        init: function () {
            templates = {
                card: function () {
                    var tmpl = BK.templates['flip-card'];
                    Mustache.parse(tmpl);
                    return tmpl;
                }()
            }
            BK.home.setupHero();
            BK.home.setupTweets();
        },
        attachEventHandlers: function () {
            if (typeof google !== 'undefined')
                BK.home.setupMap();
        },
        setupHero: function () {
            var itemsCount = $(".heroCarousel").children().length;
            $(".heroCarousel").owlCarousel({
                loop: itemsCount <= 1 ? false : true,
                nav: true,
                center: true,
                items: 1,
                navText: itemsCount <= 1 ? [] : ['<div class="hover"></div><div class="arrow"></div>', '<div class="hover"></div><div class="arrow"></div>'],
                margin: 0,
                autoplay: true,
                autoplayTimeout: 4000,
                autoplayHoverPause: false,
                smartSpeed: 500,
                dotsSpeed: 500
            });
            $('.heroCarousel .owl-controls .owl-dots .owl-dot').on('click', function (e) {
                BK.analytics.track(['send', 'event', 'carousel', 'click', 'browse']);
            });
            var itemH = $('.heroCarousel .owl-item.center').height();
            var arrowH = $('.heroCarousel .owl-controls .owl-prev .arrow').height();
            var bottom = (itemH - arrowH) / 1.6;
            $('.heroCarousel .owl-controls .owl-nav .owl-prev .arrow').css('bottom', bottom + 'px');
            $('.heroCarousel .owl-controls .owl-nav .owl-next .arrow').css('bottom', bottom + 'px');
        },
        setupTweets: function () {
            //var ua = navigator.userAgent.toLowerCase();
            //var isAndroid = ua.indexOf("android") > -1;
            //var isIphone = (ua.indexOf('iphone') != -1);
            //var isIpod = (ua.indexOf('ipod') != -1);
            //var iphone4 = (window.screen.height <= (960 / 2));
            //var iphone5 = (window.screen.height >= (1136 / 2));
            BK.home.buildFlicker();
        },
        buildFlicker: function () {
            var $wrapper = $('#flickWrapper');            
            var mqMobileMatch = BK.getMq('mobile').matches;
            var mqTabletMatch = BK.getMq('tablet').matches;            
            $.when($.getJSON(base_url + 'Home/InstaPhoto')).then(function (instagramResponse) {
                var instas = instagramResponse[0],
                    items = [],
                    i = 0,
                    a, b;
                a = instagramResponse;
                for (; i < a.length; i++) {
                    if ((mqMobileMatch || mqTabletMatch) && items.length >= 10)
                        continue;
                    items.push(a[i]);
                }
                if (a.length < 4) {                    
                    items.push(a[0]);
                    items.push(a[1]);
                    items.push(a[2]);
                } else if (a.length < 3) {
                    items.push(a[0]);
                    items.push(a[1]);
                    items.push(a[2]);
                    items.push(a[0]);
                    items.push(a[1]);
                    items.push(a[2]);
                } else if (a.length < 2) {
                    items.push(a[0]);
                    items.push(a[1]);
                    items.push(a[2]);
                    items.push(a[0]);
                    items.push(a[1]);
                    items.push(a[2]);
                }
                $wrapper.append(Mustache.render(templates.card, {
                    items: items
                }));
            }).done(function () {
                var $ul = $wrapper.find('ul'),
                    $li = $wrapper.find('li'),
                    totalWidth = $li.length * $li.eq(0).outerWidth(true);
                $ul.width(totalWidth);                
                bkFlicker = new Inflickity($wrapper[0], {
                    friction: 0.05,
                    animationDuration: 300
                });                
                $wrapper.on('click touchend', '.flipContainer', BK.home.checkScroll);
            });
        },
        checkScroll: function () {            
            var $clickedEl = $(this);            
            setTimeout(function () {                
                BK.home.flipCard($clickedEl)                
            }, 50);
        },
        flipCard: function ($clickedEl) {
            if (bkFlicker.isScrolling === false || bkFlicker.isScrolling === 'undefined') {
                var index = $clickedEl.parent().index();                
                $('.flick').find('> .item:eq(' + index + ') > .flipContainer').toggleClass('hover');
            }
        }
    }
}();
BK = BK || {};
BK.other = function () {
    return {
        init: function () {
            BK.other.setupHero();
        },
        setupHero: function () {
            $(".heroCarousel").owlCarousel({
                autoPlay: 4000,
                slideSpeed: 500,
                paginationSpeed: 500,
                singleItem: true
            });
        }
    }
}();
BK = BK || {};
BK.nav = function () {
    var $mainNav = $('.mainNav');
    var currentForm = null;
    return {
        init: function () {
            BK.nav.attachEventHandlers();
        },
        working: function (tf) {
            if (tf) {
                $('body').addClass('wait');
                $(this).addClass('wait');
            } else {
                $('body').removeClass('wait').addClass('doneWait');
                $(this).removeClass('wait').addClass('doneWait');
            };
        },
        processLocationsTopLink: function () {
            var oldNavBehavior = false;
            if (oldNavBehavior) {
                var query = null;
                var locat = null;
                if (window.sessionStorage.getItem('user_location') != null) {
                    locat = window.sessionStorage.getItem('user_location').split(' ').join('').slice(1, -1);
                } else {
                    query = "Bugis Village"
                }
                handleGoogleMapsLink(query, locat);
            } else {
                var query = null;
                var locat = null;
                if (window.sessionStorage.getItem('user_location') !== null) {
                    BK.mapping.states.geolocated = true;
                    BK.mapping.states.geocoded = true;
                    BK.mapping.handleInputBySettings(query, locat);
                } else if (Modernizr.geolocation) {
                    BK.mapping.states.geofeature = true;
                    BK.nav.working(true);
                    BK.locations.getUsersLocationIfNeeded(function (position) {
                        if (typeof position !== 'undefined' && typeof position.coords !== 'undefined') {
                            locat = BK.locations.storeUserLocation(position);
                            BK.locations.isGettingUserGeo = false;
                            BK.mapping.states.geolocated = true;
                        };
                        BK.mapping.handleInputBySettings(query, locat)
                    });
                } else {
                    query = "Bugis Village"
                    locat = BK.mapping.normalizePositionObj(BK.mapping.default)
                    BK.locations.redirectToLocalMap(query, locat);
                }
            };
        },
        processLocationsInput: function () {
            var oldNavBehavior = false;
            if (oldNavBehavior) {
                var query = null;
                var locat = null;
                var $form = $(this).parent();
                if ($form.find('input').val().length) {
                    query = $form.find('input').val();
                } else if (window.sessionStorage.getItem('user_location') != null) {
                    locat = window.sessionStorage.getItem('user_location').split(' ').join('').slice(1, -1);
                } else {
                    query = "Bugis Village"
                }
                handleGoogleMapsLink(query, locat);
            } else {
                var query = null;
                var locat = null;
                var $form = BK.nav.currentForm;
                BK.nav.working(true);
                if ($form.find('input').val().length) {
                    query = $form.find('input').val();
                    if (BK.mapping.useStringLocation) {
                        BK.locations.redirectToLocalMap(query, locat);
                    } else {
                        BK.mapping.geocode(query, function () {
                            locat = BK.mapping.getPositionObject();
                            BK.mapping.geocoded = true;
                            BK.mapping.geolocated = true;
                            BK.locations.redirectToLocalMap(query, locat);
                        })
                    };
                } else if (window.sessionStorage.getItem('user_location') !== null) {
                    BK.mapping.states.geocoded = true;
                    BK.mapping.states.geolocated = true;
                    BK.mapping.handleInputBySettings(query, locat)
                } else if (Modernizr.geolocation) {
                    BK.mapping.states.geofeature = true;
                    BK.nav.working(true);
                    BK.locations.getUsersLocationIfNeeded(function (position) {
                        if (typeof position !== 'undefined' && typeof position.coords !== 'undefined') {
                            BK.locations.storeUserLocation(position);
                            BK.locations.isGettingUserGeo = false;
                            BK.mapping.states.geolocated = true;
                        };
                        BK.mapping.handleInputBySettings(query, locat)
                    })
                } else {
                    query = "Bugis Village";
                    BK.locations.redirectToLocalMap(query, locat);
                }
            };
        },
        attachEventHandlers: function () {
            var mqMobileMatch = BK.getMq('mobile').matches;
            BK.getMq('mobile').addListener(function (mql) {
                mqMobileMatch = mql.matches;
                if (mqMobileMatch) {
                    $mainNav.find('.formArea').removeAttr('style');
                    $mainNav.find('.navInput').removeAttr('style');
                } else {
                    $mainNav.show();
                    $mainNav.find('.subNav').hide().parent('li').removeClass('expanded');
                }
            });
            $('.mobileMenu').on('click', function () {
                var $mainNav = $('.mainNav');
                if ($mainNav.is(':visible')) {
                    $mainNav.slideUp();
                    $(this).removeClass('expanded');
                } else {
                    $mainNav.slideDown();
                    $(this).addClass('expanded');
                }
            });
            $('.subNavToggle').on('click', function (e) {
                if (mqMobileMatch) {
                    e.preventDefault();
                    $(this).parent('li').toggleClass('expanded').find('> .subNav').slideToggle();
                }
            })
            $('#mainNav .hasForm').on('click', '> a', function (e) {
                e.preventDefault();
                var $closestLi = $(this).closest('li'),
                    $formArea = $(this).next(),
                    $formInput = $formArea.find('.navInput'),
                    $formSubmit = $formArea.find('.navInputSubmit');
                if ($closestLi.hasClass('formVisible')) {
                    $formArea.animate({
                        left: '100%',
                        avoidCSSTransitions: true
                    });
                    $closestLi.removeClass('formVisible');
                } else {
                    $formInput.outerWidth($closestLi.outerWidth() - $formSubmit.outerWidth());
                    $formArea.outerWidth($formInput.outerWidth() + $formSubmit.outerWidth());
                    $formArea.animate({
                        left: '0',
                        avoidCSSTransitions: true
                    });
                    $closestLi.addClass('formVisible');
                }
            });
            $('.footerLinks h4').on('click', function (e) {
                if (mqMobileMatch) {
                    $(this).toggleClass('expanded').next().slideToggle();
                }
            });

            function handleGoogleMapsLink(query, locat) {
                var buildStr = "https://www.google.com/maps/search/" + ((query != null) ? query : "") + "+Burger+King/" + ((locat != null) ? '@' + locat : '');
                window.open(buildStr, '_blank');
            }
            var oldNavBehavior = false;
            $('form[action="' + base_url + 'Locator/Index"]').find('button[type="submit"]').on("click", function (e) {
                e.preventDefault();
                BK.nav.currentForm = $(this).parent();
                if (typeof google !== 'object' || typeof google.maps !== 'object') {;
                    BK.locations.loadGoogleMapsAPI('BK.nav.processLocationsInput');
                } else {
                    BK.nav.processLocationsInput();
                }
            });
            $('nav .location a').click(function (e) {
                e.preventDefault();
                if (typeof google !== 'object' || typeof google.maps !== 'object') {;
                    BK.locations.loadGoogleMapsAPI('BK.nav.processLocationsTopLink');
                } else {
                    BK.nav.processLocationsTopLink();
                }
            });
            $('#toTop').on('click', function (e) {
                e.preventDefault();
                $('html, body').animate({
                    scrollTop: 0
                }, 500);
            });
            //$('.nav_deliver').click(function (e) {
            //    e.preventDefault();
            //    console.log(navigator.userAgent);
            //    if (navigator.userAgent.toLowerCase().indexOf("android") > -1) {
            //        window.location.href = 'https://play.google.com/store/apps/details?id=com.oddle.burkerkingcustomerapp';
            //    } else if (navigator.userAgent.toLowerCase().indexOf("iphone") > -1) {
            //        window.location.href = 'https://itunes.apple.com/sg/app/burger-king-singapore/id1233020916?mt=8';
            //    } else {
            //        window.location.href = $(this).attr("href");
            //    }
            //});
        }
    }
}();
BK = BK || {};
BK.productDetail = function () {
    return {
        init: function () {
            BK.productDetail.attachEventHandlers();
            $('.nutrition-form').each(function () {
                new BKNutritionInfo(this);
            });
            $('.select-menu').each(function () {
                $(this).data('selectMenu', new BKSelectMenu(this));
            });
        },
        attachEventHandlers: function () { },
        showNutritionInfo: function (id) {
            $('.nutrition-info').removeClass('active');
            $('#' + id).addClass('active');
        }
    }
}();
BKNutritionInfo = function (el) {
    this.$el = $(el);
    this.$items = this.$el.find('.nutrition-item');
    this.allergens = [];
    this.calc = new BKNutritionCalc();
    this.productHasVariants = this.$el.data('productHasVariants') || false;
    this.productHasIngredients = this.$el.data('productHasIngredients') || false;
    if (this.productHasIngredients) {
        this.ingredientCalc = new BKNutritionCalc();
    }
    this.templates = {
        nutrition: function () {
            var tmpl = BK.templates['mymeal-nutrition'];
            Mustache.parse(tmpl);
            return tmpl;
        }()
    };
    this.attachEventHandlers();
    var query = window.location.search;
    if (query && query.length > 1) {
        this.$el.addClass('isUpdate');
        var allParams = query.substr(1).split('&'),
            i = 0;
        for (; allParams[i]; i++) {
            var param = allParams[i].split('=');
            if (param[0] === 'idx') {
                this.idx = param[1];
            }
            if (param[0] === 'excluded') {
                this.setExcludedIngredients(param[1]);
            }
            if (param[0] === 'variant') {
                this.$el.find('.nutrition-info-set-variant[value=' + param[1] + ']').trigger('click');
            }
        }
    }
    this.setData().render();
    return this;
};
BKNutritionInfo.prototype = {
    attachEventHandlers: function () {
        var self = this;
        self.$el.on('submit', function _onNutritionFormSubmit(e) {
            e.preventDefault();
        });
        self.$el.on('click', '.nutrition-add', function _onNutritionAddClick(e) {
            e.preventDefault();
            self.addToMeal();
        });
        self.$el.on('click', '.nutrition-update', function _onNutritionUpdateClick(e) {
            e.preventDefault();
            self.updateMeal();
        });
        self.$el.on('click', '.nutrition-info-set-variant', function _onNutritionNavClick(e) {
            e.preventDefault();
            var $this = $(this);
            self.$el.find('.nutrition-info-set-variant').removeClass('active');
            $this.addClass('active');
            self.setNutritionInfoVariant($this.val());
            self.setData().render();
        });
        self.$el.on('change', '.nutrition-item', function _onNutritionItemChange(e) {
            var $this = $(this);
            self.setData().render();
        });
        return self;
    },
    getExcludedIngredients: function () {
        var self = this,
            a = [];
        self.$items.filter('input[type=radio].nutrition-ingredient').not('input:checked').each(function () {
            a.push(BK_PRODUCT_NUTRITION[this.value]['id']);
        });
        return a;
    },
    setExcludedIngredients: function (str) {
        var excluded = str.split(','),
            i = 0;
        for (; excluded[i]; i++) {
            this.$el.find('input[value=' + excluded[i] + ']').trigger('click');
        }
    },
    getCustomProduct: function (data, excludes) {
        var self = this;
        self.ingredientCalc.clear();
        self.ingredientCalc.addItem(data);
        var i = 0,
            j = excludes.length;
        for (; i < j; i++) {
            self.ingredientCalc.subtractItem(BK_PRODUCT_NUTRITION[excludes[i]]);
        }
        var customSandwich = $.extend({}, data, self.ingredientCalc.getTotals());
        customSandwich.label += ' (Custom)';
        return customSandwich;
    },
    getData: function () {
        var items = [];
        if (this.productHasVariants) {
            var variants = this.$items.filter('input.nutrition-variant-item:checked'),
                i = 0,
                variantData;
            for (; variants[i]; i++) {
                variantData = BK_PRODUCT_NUTRITION[variants[i].value];
                if (variantData) items.push(variantData);
            }
        }
        if (this.productHasIngredients) {
            var productId = this.$items.filter('input.nutrition-ingredient-parent').val();
            var productData = BK_PRODUCT_NUTRITION[productId];
            var excludes = this.getExcludedIngredients();
            if (excludes.length) {
                productData = this.getCustomProduct(productData, excludes);
            }
            if (productData) items.push(productData);
        }
        return items;
    },
    setData: function () {
        var self = this;
        self.calc.clear();
        self.$items.each(function _forEachNutritionItem() {
            var $item = $(this);
            if ($item.is('input[type=hidden].nutrition-ingredient') || $item.is('input.nutrition-variant-item:checked') || $item.is('input.nutrition-ingredient:checked')) {
                var data = BK_PRODUCT_NUTRITION[$item.val()];
                if ('allergens' in data) {
                    self.allergens = self.allergens.concat(data.allergens);
                }
                self.calc.addItem(data);
            } else if ($item.is('input.nutrition-ingredient-parent')) {
                var data = BK_PRODUCT_NUTRITION[$item.val()];
                if ('allergens' in data) {
                    self.allergens = self.allergens.concat(data.allergens);
                }
            }
        });
        return self;
    },
    setNutritionInfoVariant: function (size) {
        this.$items.each(function _forEachOption() {
            var $option = $(this),
                id = $option.data(size + 'Id');
            if (id) {
                $option.val(id);
                if ($option.is('.select-menu-option-input')) {
                    $option.next('.select-menu-option-label').text(BK_PRODUCT_NUTRITION[id].label);
                    if ($option.is('input:checked')) {
                        $option.closest('.select-menu').find('.select-menu-label').text(BK_PRODUCT_NUTRITION[id].label);
                    }
                }
            }
        });
        return this;
    },
    addToMeal: function () {
        BK.mymeal.addItems(this.getData(), true).render();
        return this;
    },
    updateMeal: function () {
        BK.mymeal.updateItem(this.getData()[0], this.idx).render();
        return this;
    },
    render: function () {
        var nutrition = Mustache.render(this.templates.nutrition, {
            nutrition: this.calc.getRoundedTotals(),
            allergens: BK.util.getUniqueArray(this.allergens).join(", "),
            isMyMeal: false,
            isVisible: true
        });
        this.$el.next('.nutrition-content').replaceWith(nutrition);
        return this;
    }
};

function BKSelectMenu(el) {
    this.$el = $(el);
    this.$label = this.$el.find('.select-menu-label');
    this.$value = this.$el.find('.select-menu-value');
    this.attachEventHandlers();
    return this;
};
BKSelectMenu.prototype = {
    attachEventHandlers: function () {
        var self = this;
        self.$el.on('change', '.select-menu-option-input', function () {
            var $option = $(this);
            $label = $option.next();
            self.$value.val($option.val());
            self.$label.text($label.text()).trigger('click');
        });
        return self;
    }
};
BK = BK || {};
BK.mymeal = function () {
    var store = window.sessionStorage,
        templates = {},
        cachedData = [],
        calc = new BKNutritionCalc();
    return {
        $el: null,
        init: function () {
            templates = {
                modal: function () {
                    var tmpl = BK.templates['mymeal-modal'];
                    Mustache.parse(tmpl);
                    return tmpl;
                }(),
                items: function () {
                    var tmpl = BK.templates['mymeal-items'];
                    Mustache.parse(tmpl);
                    return tmpl;
                }(),
                nutrition: function () {
                    var tmpl = BK.templates['mymeal-nutrition'];
                    Mustache.parse(tmpl);
                    return tmpl;
                }()
            };
            this.addItems(BK.mymeal.getStoredData()).render();
            return this;
        },
        attachEventHandlers: function () {
            var self = this;
            self.$el.on('click', '.delete', function _onMyMealItemDelete(e) {
                e.preventDefault();
                self.deleteItem($(this).data('itemIndex')).render();
            });
            self.$el.on('shown.bs.modal', function _onBSModalShown(e) {
                $('body').addClass('mymeal-is-active');
            });
            self.$el.on('hide.bs.modal', function _onBSModalShown(e) {
                $('body').removeClass('mymeal-is-active');
            });
            self.$el.on('click', '.bk-btn-print', function _onPrintClick(e) {
                window.print();
            });
            return this;
        },
        getStoredData: function () {
            return JSON.parse(store.getItem('bk_mymeal_data')) || [];
        },
        setStoredData: function () {
            store.setItem('bk_mymeal_data', JSON.stringify(cachedData));
            return this;
        },
        addItems: function (items, store) {
            if (items.length) {
                var i = 0,
                    j = items.length;
                for (; i < j; i++) {
                    calc.addItem(items[i]);
                    cachedData.push(items[i]);
                }
                if (store) this.setStoredData();
            }
            return this;
        },
        updateItem: function (item, index) {
            calc.subtractItem(cachedData[index]);
            cachedData[index] = item;
            calc.addItem(cachedData[index]);
            this.setStoredData();
            return this;
        },
        deleteItem: function (index) {
            if (cachedData[index]) {
                calc.subtractItem(cachedData[index]);
                cachedData.splice(index, 1);
                this.setStoredData();
            }
            return this;
        },
        render: function () {
            if (this.$el) {
                this.$el.find('.items-table').replaceWith(this.renderItems());
                this.$el.find('.nutrition-content').replaceWith(this.renderNutrition());
            } else {
                var modal = Mustache.render(templates.modal, {
                    nutrition: this.renderNutrition(),
                    items: this.renderItems()
                });
                this.$el = $(modal);
                this.$el.appendTo('body');
                this.attachEventHandlers();
            }
            return this;
        },
        renderItems: function () {
            for (var i in cachedData) {
                cachedData[i]['idx'] = Number(i);
                cachedData[i]['roundedCalories'] = calc.round('calories', cachedData[i].calories);
            }
            return Mustache.render(templates.items, {
                items: cachedData,
                totalCalories: calc.getRoundedTotals('calories'),
                params: function () {
                    return function (text, render) {
                        var out = '',
                            p = [];
                        p.push('idx=' + this.idx);
                        if (this.variant) p.push('variant=' + this.variant);
                        if (this.excluded && this.excluded.length) p.push('excluded=' + this.excluded.join(','));
                        out = '?' + p.join('&');
                        return render(out);
                    }
                }
            });
        },
        renderNutrition: function () {
            var allergens = [];
            for (var i in cachedData) {
                if ('allergens' in cachedData[i]) {
                    allergens = allergens.concat(cachedData[i].allergens);
                }
            }
            return Mustache.render(templates.nutrition, {
                nutrition: calc.getRoundedTotals(),
                allergens: BK.util.getUniqueArray(allergens).join(", "),
                isVisible: !!cachedData.length,
                isMyMeal: true
            });
        }
    };
}();
BK = BK || {};
BK.mapping = function () {
    return {
        states: {
            'geofeature': false,
            'geolocated': false,
            'geocoded': false,
            'searching': false,
            'errorGeo': false,
            'myBk': false
        },
        state: '',
        useStringLocation: false,
        useSingleCoord: false,
        default: {
            //lat: 1.300341,
            //lng: 103.855286
            lat: 0,
            lng: 0
        },
        urlParamString: 'field_geofield_distance',
        urlParamStringSuffix: '[origin]',
        urlParamCoords: 'bklocation_coords',
        urlParamLat: 'field_geofield_distance[origin][lat]',
        urlParamLng: 'field_geofield_distance[origin][lon]',
        urlCoordsSplit: true,
        urlField: function () {
            if (this.useStringLocation) {
                return this.urlParamString + this.urlParamStringSuffix;
            } else if (!this.useSingleCoord) {
                return this.urlParamLat + "=&" + this.urlParamLng;
            } else {
                return this.urlParamCoords;
            };
        },
        hasParam: function () {
            var fieldName = this.urlField();
            if (!this.useSingleCoord) {
                fieldName = fieldName.split('&')[0].replace('[origin][lat]=', '');
            };
            
            if (document.location.search.indexOf(fieldName) !== -1) {
                this.states.searching = true;
                this.state = 'searching';
                return true;
            } else {
                return false;
            };
        },
        setLocationCoordsString: function (lat, lon) {
            var coordsQuery = '';
            var query;
            var params = getQueryParams(window.location.search);
            if (typeof params["search"] != "undefined") {
                query = params["search"];
            } else {
                query = $('.locInput input').val();
                
            }
            

            if (!this.useSingleCoord) {
                coordsQuery = this.urlField().replace(this.urlParamLat + "=", this.urlParamLat + "=" + lat);
                coordsQuery = coordsQuery.replace(this.urlParamLng, this.urlParamLng + "=" + lon);
            };

            if (query == "") {
                return base_url + 'Locator/Index?' + coordsQuery;
            } else {
                debugger;
                return base_url + 'Locator/Index?' + coordsQuery + '&locationSearch=' + encodeURIComponent(query);
            }

        },
        options: function (lat, lng) {
            return {
                center: new google.maps.LatLng(lat, lng),
                zoom: 11,
                scrollwheel: false,
                mapTypeControl: false,
                panControl: true,
                panControlOptions: {
                    position: google.maps.ControlPosition.RIGHT_TOP
                },
                zoomControl: true,
                zoomControlOptions: {
                    style: google.maps.ZoomControlStyle.LARGE,
                    position: google.maps.ControlPosition.RIGHT_TOP
                },
                scaleControl: true,
                streetViewControl: true,
                streetViewControlOptions: {
                    position: google.maps.ControlPosition.RIGHT_TOP
                },
                styles: [{
                    featureType: "water",
                    elementType: "geometry",
                    stylers: [{
                        color: '#6bade3'
                    }]
                }, {
                    featureType: "poi.park",
                    elementType: "geometry",
                    stylers: [{
                        color: '#a3d55f'
                    }]
                }]
            };
        },
        handleInputBySettings: function (query) {
            if (!BK.mapping.useStringLocation) {
                BK.locations.redirectToLocalMap(query, BK.mapping.getPositionString());
            } else {
                if (window.sessionStorage.getItem('user_address') !== null && query === '') {
                    BK.locations.redirectToLocalMap(window.sessionStorage.getItem('user_address'))
                } else {
                    BK.mapping.reverseGeocode(BK.mapping.getPositionObject(), function () {
                        var query = BK.mapping.address;
                        BK.locations.redirectToLocalMap(query);
                    })
                };
            };
        },
        normalizePositionObj: function (position) {
            var newPos = {
                coords: {}
            };
            if (typeof position.lat !== 'undefined' && typeof position.lng !== 'undefined') {
                newPos.coords.latitude = BK.util.resultOf(position, 'lat');
                newPos.coords.longitude = BK.util.resultOf(position, 'lng');
                return newPos;
            } else {
                return position;
            }
        },
        address: '',
        reverseGeocode: function (latlong, callback) {
            BK.mapping.isGettingUserGeo = true;
            var geocoder = new google.maps.Geocoder();
            var latlng = BK.mapping.getPositionObject(latlong);
            geocoder.geocode({
                'latLng': latlng
            }, function (results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    if (results[2]) {
                        BK.mapping.address = results[2].formatted_address;
                        window.sessionStorage.setItem('user_address', BK.mapping.address);
                    }
                } else {
                    console.warn('Error performing reverse geocoding.')
                }
                BK.mapping.isGettingUserGeo = false;
                callback();
            });
        },
        geocode: function (address, callback) {
            BK.mapping.isGettingUserGeo = true;
            var geocoder = new google.maps.Geocoder();
            var latlng;
            geocoder.geocode({
                'address': address
            }, function (results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    latlng = results[0].geometry.location;
                    BK.locations.storeUserLocation(latlng);
                } else {
                    console.warn('Error performing geocoding of string location.');
                }
                BK.mapping.isGettingUserGeo = false;
                callback(latlng);
            })
        },
        map: false,
        center: {},
        getPositionObject: function (latlngString) {
            var lat;
            var lng;
            var latlng;
            if (typeof latlngString === 'object') {
                latlngString = BK.mapping.normalizePositionObj(latlngString);
                lat = latlngString.coords.latitude;
                lng = latlngString.coords.longitude;
            } else {
                var userLocationAsString = (typeof latlngString === 'undefined') ? window.sessionStorage.getItem('user_location') : latlngString;
                var latLngAsArray = userLocationAsString.split(",", 2);
                lat = parseFloat(latLngAsArray[0].substring(1, latLngAsArray[0].length));
                lng = parseFloat(latLngAsArray[1].substring(0, latLngAsArray[1].length - 1));
            };
            latlng = new google.maps.LatLng(lat, lng);
            BK.mapping.states.geolocated = true;
            return latlng;
        },
        getPositionString: function (val) {
            var place;
            if (typeof val === 'undefined' || window.sessionStorage.getItem('user_location') !== null) {
                place = window.sessionStorage.getItem('user_location');
            } else {
                place = val.toString();
            }
            return place;
        },
        setCenter: function (thisMap) {
            thisMap.setCenter(BK.mapping.center);
        },
        buildMap: function (lat, lng) {
            var mapOptions = BK.mapping.options(lat, lng)
            var thisMap = new google.maps.Map(document.getElementById("locationsMap"), mapOptions);
            BK.mapping.map = thisMap;
            var setListeners = (function (aMap) {
                google.maps.event.addDomListener(aMap, 'idle', function () {
                    BK.mapping.center = aMap.getCenter();
                });
                google.maps.event.addDomListenerOnce(aMap, 'bounds_changed', function () {
                    BK.locations.list.init();
                })
                google.maps.event.addDomListener(window, 'resize', function () {
                    BK.mapping.setCenter(aMap);
                });
            })(thisMap);
            return thisMap;
        }
    }
}();
BK = BK || {};
var page = 1;
 BK.locations = function () {
    var locationsMap, center, markersArray = [],
        myLocationCookie, templates = {},
        $xml, $locationsList = $('#locationsList'),
            $storeList = $('div.bk-restaurants li').length;
    $.cookie.json = true;
    return {
        isGettingUserGeo: false,
        init: function () {
            templates = {
                address: function () {
                    var tmpl = BK.templates['location-address'];
                    Mustache.parse(tmpl);
                    return tmpl;
                }()
            }
            if (window.sessionStorage.getItem('user_location') != null) {
                BK.mapping.states.geocoded = true;
            };
            BK.locations.getUsersLocationIfNeeded(BK.locations.preMapInit);
            BK.locations.attachEventHandlers();
        },
        list: function () {
            var selector = 'div.bk-restaurants li';
            var divLat = 'div.bk-latitude';
            var divLong = 'div.bk-longitude';
            var results = [];
            var foundItems = [];
            var item;
            return {
                found: foundItems,
                init: function () {
                    var thisMap = BK.mapping.map;
                    var that = this;
                    if (foundItems.length === 0) {
                        this.collectResults(function () {
                            that.setBoundsToContain(thisMap);
                        });
                    };
                },
                collectResults: function (callback) {
                    results = $(selector);
                    if (results.length) {
                        results.each(function (i) {
                            item = {
                                lat: $(this).find(divLat).text(),
                                lng: $(this).find(divLong).text()
                            }
                            item.latlng = new google.maps.LatLng(item.lat, item.lng);
                            foundItems.push(item);
                        });
                        callback();
                    };
                },
                setBoundsToContain: function (thisMap) {
                    if (thisMap !== false) {
                        var bounds = thisMap.getBounds();
                        var newBounds = new google.maps.LatLngBounds();
                        $.each(this.found, function (i, val) {
                            newBounds.extend(this.latlng);
                        });
                        if (newBounds.getNorthEast().equals(newBounds.getSouthWest())) {
                            var extendPoint1 = new google.maps.LatLng(newBounds.getNorthEast().lat() + 0.01, newBounds.getNorthEast().lng() + 0.01);
                            var extendPoint2 = new google.maps.LatLng(newBounds.getNorthEast().lat() - 0.01, newBounds.getNorthEast().lng() - 0.01);
                            newBounds.extend(extendPoint1);
                            newBounds.extend(extendPoint2);
                        };
                        thisMap.fitBounds(newBounds);
                        BK.mapping.center = thisMap.getCenter();
                    };
                }
            }
        }(),
        attachEventHandlers: function () {
            //$('.locationsResults').on('click', '.makeMyLocation', BK.locations.makeDefaultBk);
            //$('.locInput .submit').click(function (e) {
            //    e.preventDefault();
            //    var query = $('.locInput input').val();
            //    var locat = null;
            //    BK.nav.working(true);
            //    if (query.length) {
            //        if (BK.mapping.useStringLocation) {
            //            BK.locations.redirectToLocalMap(query);
            //        } else {
            //            BK.mapping.geocode(query, function () {
            //                locat = BK.mapping.getPositionObject();
            //                BK.mapping.geocoded = true;
            //                BK.mapping.geolocated = true;
            //                BK.locations.redirectToLocalMap(query, locat);
            //            })
            //        }                    
            //    } else if (window.sessionStorage.getItem('user_location') !== null) {
            //        BK.mapping.states.geocoded = true;
            //        BK.mapping.states.geolocated = true;
            //        BK.mapping.handleInputBySettings(query, locat)
            //    } else if (Modernizr.geolocation) {
            //        BK.mapping.states.geofeature = true;
            //        BK.nav.working(true);
            //        BK.locations.getUsersLocationIfNeeded(function (position) {
            //            if (typeof position !== 'undefined' && typeof position.coords !== 'undefined') {
            //                BK.locations.storeUserLocation(position);
            //                BK.locations.isGettingUserGeo = false;
            //                BK.mapping.states.geolocated = true;
            //            };
            //            BK.mapping.handleInputBySettings(query, locat)
            //        })
            //    } else {
            //        query = "Selangor";
            //        BK.locations.redirectToLocalMap(query, locat);
            //    }
            //});
        },
        makeDefaultBk: function (e) {
            e.preventDefault;
            var myId = $(this).closest('.location').data('restaurantId'),
                myLocation = $('.bk-id:contains(' + myId + ')').parent(),
                myBkCookie = {
                    id: myId,
                    address1: myLocation.children('.bk-address1').text(),
                    city: myLocation.children('.bk-city').text(),
                    state: myLocation.children('.bk-state').text(),
                    zip: myLocation.children('.bk-zip').text(),
                    weekdayStoreHours: myLocation.children('.bk-weekday-hours').text(),
                    weekendStoreHours: myLocation.children('.bk-weekend-hours').text()
                };
            myLocationCookie = $.cookie('bkMyLocation', myBkCookie, {
                expires: 365
            });
            BK.locations.clearMarkers(BK.locations.drawMarkers);
            BK.popLocation();
            return false;
        },
        redirectToLocalMap: function (query, locat) {
            if ((query !== 'undefined' && typeof query !== 'undefined') && BK.mapping.useStringLocation) {
                sendUser(encodeURIComponent(query));
            } else if ((locat === null || locat === '') && (BK.mapping.states.geocoded || BK.mapping.states.geolocated) && !BK.mapping.useStringLocation) {
                sendUser(BK.mapping.getPositionString());
            } else if ((locat !== '' && typeof locat !== 'undefined') && (BK.mapping.states.geocoded || BK.mapping.states.geolocated) && !BK.mapping.useStringLocation) {
                sendUser(BK.mapping.normalizePositionObj(BK.mapping.getPositionString(locat)));
            } else if (BK.mapping.states.errorGeo) {
                var place;
                if (BK.mapping.useStringLocation) {
                    place = 'Bugis Village';
                } else {
                    place = "(" + BK.mapping.default.lat + "," + BK.mapping.default.lng + ")";
                    if (!BK.mapping.useSingleCoord) {
                        place = BK.mapping.getPositionObject(place);
                    };
                };
                sendUser(place);
            } else {
                sendUser();
            }

            function sendUser(locateString) {
                if (typeof locateString !== 'undefined' && locateString !== 'undefined') {
                    if (typeof locateString === 'object' && BK.mapping.useStringLocation || BK.mapping.useSingleCoord) {
                        locateString = locateString.toString();
                        window.location = base_url + 'Locator/index?' + BK.mapping.urlField() + '=' + locateString;
                    } else if (!BK.mapping.useSingleCoord) {
                        locateString = BK.mapping.getPositionObject(locateString);
                        window.location = BK.mapping.setLocationCoordsString(locateString.lat(), locateString.lng());
                    };
                } else {
                    window.location = base_url + 'Locator/index';
                };
            }
            BK.nav.working(false);
        },
        initLocations: function (position) {
            if (BK.locations.isGettingUserGeo) {
                return true;
            } else if (!BK.mapping.hasParam() && BK.mapping.states.geolocated) {
                BK.mapping.handleInputBySettings();
                return true;
            };

            function getURLParam(param) {
                var params = window.location.search.substring(1).split('&');
                for (var i = 0; i < params.length; i++) {
                    var name = params[i].split('=');
                    if (name[0] == param) {
                        return decodeURIComponent(name[1]);
                    }
                }
                return false;
            }
            var lat, lng, num = $('.bk-restaurants-total').text();            
            var id = $('.bk-id').text();
            var substring = window.location.origin.length + window.location.pathname.length;           
            if (num == 0) {
                lat = BK.mapping.default.lat;
                lng = BK.mapping.default.lng;
                $('.bk-location-target').text('None Found');
                $('.bk-location-total').text('0');
                $('.bk-location-results').text('0');
                $('.pagination').hide();                
            } else {
                if (typeof position !== 'undefined' && !BK.mapping.states.searching) {
                    position = BK.mapping.normalizePositionObj(position);
                    lat = position.coords.latitude;
                    lng = position.coords.longitude;
                } else {
                    lat = $('.bk-latitude').first().text();
                    lng = $('.bk-longitude').first().text();
                };
                $('.bk-location-total').text($('.bk-restaurants-total').text());
                var target = (window.location.href.match(/&target/)) ? getURLParam('target') : $('.bk-state').first().text();
                //$('.bk-location-target').text(target);                
                if (num <= 4) {
                    $('.bk-location-results').text(num);
                } else {
                    $('.bk-location-results').text($storeList);
                    //var target_param = (window.location.href.match(/&target/)) ? '' : '&target=' + target;
                    if($('.page-locations .pager-previous a').length)
                    {
                        var href=$('.page-locations .pager-previous a').attr("href");
                        $('.pagination .bk-btn-prev').attr('href',href);
                        $('.pagination .bk-btn-prev').attr('style', "");
                    }
                    if($('.page-locations .pager-next a').length)
                    {
                        var href=$('.page-locations .pager-next a').attr("href");
                        $('.pagination .bk-btn-next').attr('href',href);
                        $('.pagination .bk-btn-next').attr('style', "");
                    }
                }
            }
            locationsMap = BK.mapping.buildMap(lat, lng);
            BK.locations.drawMarkers();
        },
        getUsersLocationIfNeeded: function (callback) {
            if (BK.mapping.hasParam()) {
                BK.locations.initLocations();
            } else if (window.sessionStorage.getItem('user_location') == null) {
                if (Modernizr.geolocation) {
                    BK.mapping.states.geofeature = true;
                    var options = {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0,
                        scrollwheel: false
                    };
                    BK.locations.isGettingUserGeo = true;
                    navigator.geolocation.getCurrentPosition(callback, BK.locations.positionError, options);
                } else {
                    window.sessionStorage.removeItem('user_location');
                    callback();
                }
            } else {
                try {
                    var positionObject = BK.mapping.getPositionObject();
                    callback(positionObject);
                } catch (e) {
                    console.warn('error getting location data from sessionStorage');
                    callback()
                }
            }
        },
        positionError: function () {
            BK.nav.working(false);
            BK.locations.isGettingUserGeo = false;
            BK.mapping.states.geolocated = false;
            BK.mapping.states.errorGeo = true;
            console.warn('Error generated on navigator.geolocation lookup');
            BK.locations.redirectToLocalMap();
        },
        preMapInit: function (position) {
            if (typeof position !== 'undefined' && typeof position.coords !== 'undefined') {
                BK.locations.storeUserLocation(position);
                BK.locations.isGettingUserGeo = false;
                BK.mapping.states.geolocated = true;
            };
            BK.locations.initLocations(position)
        },
        storeUserLocation: function (position) {
            position = BK.mapping.normalizePositionObj(position)
            if (position && position.coords) {
                var latLng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
                window.sessionStorage.setItem('user_location', latLng);
            }
            return position;
        },
        drawMarkers: function (index) {
            var locations = [];
            $locationsList.empty();
            if ($.cookie('bkMyLocation')) myLocationCookie = $.cookie('bkMyLocation');
            $('.bk-restaurants li').each(function (index) {
                var lat = $('.bk-latitude', this).text(),
                    lng = $('.bk-longitude', this).text(),
                    offersDelivery = ($('.bk-delivery', this).length),
                    markerNum = 'marker' + $('.bk-counter', this).text(),
                    markerLabel = '<span class="text">' + $('.bk-num', this).text() + '</span>',
                    myBkLabel = '<span class="text">my<br/>BK</span>',
                    deliveryLabel = '<span class="getDelivery">Get Delivery <i class="icon icon_truck-white"></i></span>',
                    isMyLocation = (myLocationCookie && (String(myLocationCookie.id) === $('.bk-id', this).text()));
                var markerImg = {
                    url: base_url + 'Content/icons/icon_pindrop-orange.svg',
                    size: new google.maps.Size(43, 58),
                    scaledSize: new google.maps.Size(43, 58),
                    origin: new google.maps.Point(0, 0),
                    anchor: new google.maps.Point(22, 58)
                };
                var markerImgActive = {
                    url: base_url + 'Content/icons/icon_pindrop-blue.svg',
                    size: new google.maps.Size(43, 58),
                    scaledSize: new google.maps.Size(43, 58),
                    origin: new google.maps.Point(0, 0),
                    anchor: new google.maps.Point(22, 58)
                };
                var markerObj = {
                    position: new google.maps.LatLng(lat,lng),
                    draggable: false,
                    map: locationsMap,
                    labelClass: 'mapMarkerLabel'
                };
                if (isMyLocation) {
                    markerObj.icon = markerImgActive;
                    markerObj.labelContent = myBkLabel;
                    markerObj.labelAnchor = new google.maps.Point(7, 50);
                    markerObj.labelClass = markerObj.labelClass + ' myBk';
                } else {
                    markerObj.icon = markerImg;
                    markerObj.labelContent = markerLabel;
                    markerObj.labelAnchor = new google.maps.Point(5, 45);
                }
                if (offersDelivery) {
                    markerObj.labelContent = markerObj.labelContent + deliveryLabel;
                    markerObj.labelClass = markerObj.labelClass + ' hasDelivery';
                    markerObj.zIndex = 0;
                }
                var markerNum = new MarkerWithLabel(markerObj);
                markersArray.push(markerNum);
                locations.push(Mustache.render(templates.address, BK.locations.getLocationObj(index, this, isMyLocation)));
            });
            $locationsList.append(locations);
        },
        clearMarkers: function (callback) {
            if (markersArray) {
                for (i = 0; i < markersArray.length; i++) {
                    markersArray[i].setMap(null);
                }
                markersArray.length = 0;
                if (typeof callback === 'function') callback();
            }
        },
        loadGoogleMapsAPI: function (callback) {
            if (callback == '')
                callback = 'BK.locations.onGoogleMapsAPILoaded';
            var script = document.createElement('script');
            script.type = 'text/javascript';
            script.async = true;
            script.src = 'https://maps.googleapis.com/maps/api/js?key=AIzaSyCBTboO5O9GhDf47Vy1Cvu2QLnJ1p8GGRM&callback=' + callback;
            document.head.appendChild(script);
        },
        onGoogleMapsAPILoaded: function () { },
        getStoreHourContent: function (context) {
            var days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun", "holiday_eve", "PH"];
            var types = ["dining", "drivethru"];
            var rows = "";
            var drive_thru = $('.bk-drivethru', context).text();
            if (drive_thru == 1) {
                for (var i = 0; i < days.length; i++) {
                    var hrs = {};
                    for (var j = 0; j < types.length; j++) {
                        var selector = ".bk-location_" + days[i] + "_" + types[j];
                        var raw = $(selector, context).text();
                        hrs[types[j]] = new BK.locations.storeHour();
                        hrs[types[j]].init(raw);
                        hrs[types[j]].parse();
                    }                    
                    rows += "<tr>" + "<td><span class='dayOfWeek'>" + (days[i] == 'holiday_eve' ? "Eve of PH" : days[i] ) + ":</span></td>" + "<td><span class=''>" + hrs["dining"].getDisplayText() + "</span></td>" + "<td><span class=''>" + hrs["drivethru"].getDisplayText() + "</span></td>" + "</tr>";
                }
                var header = "<thead><tr>" + "<th class='column-day'></th>" + "<th class='column-dining'>Opening Hours</th>" + "<th class='column-drivethru'>Breakfast Hours</th>" + "</tr></thead>";
                rows = "<tbody>" + rows + "</tbody>";
                var content = "<table>" + header + rows + "</table>";
            } else {
                for (var i = 0; i < days.length; i++) {
                    var hrs = {};
                    var selector = ".bk-location_" + days[i] + "_" + types[0];
                    var raw = $(selector, context).text();
                    hrs[types[0]] = new BK.locations.storeHour();
                    hrs[types[0]].init(raw);
                    hrs[types[0]].parse();
                    rows += "<tr>" + "<td><span class='dayOfWeek'>" + (days[i] == 'holiday_eve' ? "Eve of PH" : days[i]) + ":</span></td>" + "<td><span class=''>" + hrs["dining"].getDisplayText() + "</span></td></tr>";
                }
                var header = "<thead><tr>" + "<th class='column-day'></th>" + "<th class='column-dining'>Opening Hours</th></tr></thead>";
                rows = "<tbody>" + rows + "</tbody>";
                var content = "<table>" + header + rows + "</table>";
            }
            return content;
        },
        getDetailsPageUrl: function (context) {
            var url = "";
            var state = $('.bk-state', context).text();
            var city = $('.bk-city', context).text();
            var address1 = $('.bk-address1', context).text();
            var id = $('.bk-id', context).text();
            var prefix = base_url + "Locator/Details/";
            state = state.toLowerCase();
            city = BK.utils.toSeoFriendly(city);
            page = BK.utils.toSeoFriendly(address1 + " " + id);
            //url = prefix + "/" + state + "/" + city + "/" + page + ".html";
            url = prefix + id;
            return url;
        },
        addDetailsUrl: function (id, url) {
            //$.ajax({
            //    type: 'HEAD',
            //    url: url,
            //    success: function (request, msg, args) {
            //        var anchor = $(".locationsResults .locationsList div.location[data-restaurant-id=" + id + "] a.more-info");
            //        anchor.attr('href', url);
            //    },
            //    error: function (request, status, error) {
            //        var anchor = $(".locationsResults .locationsList div.location[data-restaurant-id=" + id + "] a.more-info");
            //        anchor.removeAttr('href');
            //        anchor.addClass('disabled');
            //    }
            //});
            return url;
        },
        getLocationObj: function (index, context, isMyLocation) {
            var title = $('.bk-title', context).text();
            var address1 = $('.bk-address1', context).text(),
                cityStateZip = $('.bk-city', context).text() + ' ' + $('.bk-state', context).text() + ' ' + $('.bk-zip', context).text(),
                directionsUrl = 'https://maps.google.com/maps?daddr=';
            var urlDirections = "Burger King, " + address1.replace(/ /g, '%20') + ', ' + cityStateZip.replace(/ /g, '%20');
            urlDirections = urlDirections.replace(/,/g, '%2C');
            urlDirections = urlDirections.replace(/[/]/g, '%2F');
            var storeHours = this.getStoreHourContent(context);
            var url = this.getDetailsPageUrl(context);
            
            var id = $('.bk-id', context).text();
            this.addDetailsUrl(id, url);
            return {
                title: title,
                num: $('.bk-num', context).text(),
                id: $('.bk-id', context).text(),
                index: $('.bk-counter', context).text(),
                isMyLocation: isMyLocation,
                offersDelivery: ($('.bk-delivery', this).length),
                street: address1,
                cityStateZip: cityStateZip,
                weekdayHours: $('.bk-weekday-hours', context).text(),
                weekendHours: $('.bk-weekend-hours', context).text(),
                phoneNumber: $('.bk-phone', context).text(),
                distance: '****',
                directionsUrl: directionsUrl + urlDirections,
                deliveryUrl: '#',
                detailsPageUrl: url,
                storeHours: storeHours
            }
        }
    }
}(); 
BK = BK || {};
BK.locations.storeHour = function () {
    var raw = "";
    var openTime = "";
    var closeTime = "";
    var open24Hours = null;
    var isClosed = null;
    return {
        init: function (raw) {
            this.raw = raw;
        },
        getDisplayText: function () {
            if (this.isClosed)
                return "Closed";
            if (this.getHour(this.openTime) == this.getHour(this.closeTime))
                return "Open 24 hours";
            if (this.openTime.indexOf("1980") != -1 || this.closeTime.indexOf("1980") != -1 || this.openTime.indexOf("1981") != -1 || this.closeTime.indexOf("1981") != -1)
                return "-";
            return this.getHour(this.openTime) + "-" + this.getHour(this.closeTime);
        },
        getHour: function (dateString) {
            var reggie = /(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})/;
            var dateArray = reggie.exec(dateString);
            var dateObject = new Date((+dateArray[1]), (+dateArray[2]) - 1, (+dateArray[3]), (+dateArray[4]), (+dateArray[5]), (+dateArray[6]));
            var format_config = Drupal.settings.locations.store_hour_format;
            var result = dateObject.format(format_config);
            if (typeof (updateHour) == 'function') {
                result = updateHour(result);
            }
            result = this.updateHour_US(result);
            return result;
        },
        updateHour_US: function (hours) {
            if (hours == "12:00 AM")
                hours = "Midnight";
            return hours;
        },
        //getHour_01: function (dateString) {
        //    var reggie = /(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})/;
        //    var dateArray = reggie.exec(dateString);
        //    var dateObject = new Date((+dateArray[1]), (+dateArray[2]) - 1, (+dateArray[3]), (+dateArray[4]), (+dateArray[5]), (+dateArray[6]));
        //    var minutes = (dateObject.getMinutes() < 10 ? '0' : '') + dateObject.getMinutes();
        //    return dateObject.getHours() + ":" + minutes;
        //},
        parse: function () {
            var strs = this.raw.split(";");
            this.openTime = strs[0];
            this.closeTime = strs[1];
            this.open24Hours = strs[2] == "1" ? true : false;
            this.isClosed = strs[3] == "1" ? true : false;
        }
    }
};
BK = BK || {};
BK.menu = function () {
    var templates = {};

    function findRightMost(item) {
        var top = item.offset().top,
            rightMost;
        BK.menu.items.filter(function (index) {
            if ($(this).offset().top === top) {
                rightMost = this;
            }
        });
        return $(rightMost);
    }
    return {
        items: false,
        detail: {
            $el: false,
            open: function ($item) {
                var html = BK.menu.render(BK_MENU_PRODUCTS[$item.data('productId')]);
                findRightMost($item).after(html);
                BK.menu.detail.$el = $('#product-dropdown');
                BK.menu.detail.$el.offset();
                BK.menu.detail.$el.show().animate({
                    minHeight: $(BK.menu.detail.$el.find(".content")[0]).height(),
                    height: $(BK.menu.detail.$el.find(".content")[0]).height()
                }, 500, 'swing', function () {
                    BK.menu.detail.$el.show().animate({
                        minHeight: $(BK.menu.detail.$el.find(".content")[0]).height(),
                        height: $(BK.menu.detail.$el.find(".content")[0]).height()
                    }, 500, 'swing');
                });
                $('html,body').animate({
                    scrollTop: $(BK.menu.detail.$el).offset().top
                }, 500);
                BK.menu.items.removeClass('active');
                $item.addClass('active');
            },
            close: function (callback) {
                var callback = callback || function () {
                    return
                };
                BK.menu.detail.$el.animate({
                    height: 0
                }, 500, 'swing', function () {
                    BK.menu.items.removeClass('active');
                    BK.menu.detail.$el.remove();
                    callback();
                });
            }
        },
        init: function () {
            this.items = $('.food-item-block');
            templates = {
                detail: function () {
                    var tmpl = BK.templates['product-detail'];
                    Mustache.parse(tmpl);
                    return tmpl;
                }()
            };
            this.attachEventHandlers();
        },
        attachEventHandlers: function () {
            var self = this;
            self.items.on('click', self.handleMenuItem);
            BK.getMq('mobile').addListener(function (mql) {
                if (self.items.filter('.active').length) {
                    self.detail.$el.hide().remove();
                    self.detail.open(BK.menu.items.filter('.active'));
                }
            });
            $('body').on('click', '#product-dropdown .close', self.handleItemDetailClose);
        },
        handleItemDetailClose: function (e) {
            e.preventDefault();
            BK.menu.detail.close();
        },
        handleMenuItem: function (e) {
            var $this = $(this),
                self = BK.menu;
            self.detail.$el = $('#product-dropdown');
            if (self.detail.$el.length) {
                self.detail.close(function () {
                    if (self.detail.$el.data('productId') !== $this.data('productId')) {
                        self.detail.open($this);
                    }
                });
            } else {
                self.detail.open($this);
            }
        },
        render: function (data) {
            return Mustache.render(templates.detail, data);
        }
    }
}();
BK = BK || {};
BK.utils = function () {
    var temp = "";
    return {
        toSeoFriendly: function (s) {
            s = s.toLowerCase();
            s = s.replace("&amp;", " and ").replace("&", " and ");
            s = s.replace(/<(?:.|\n)*?>/gm, '');
            s = s.replace(/[^a-z0-9\s\-]/g, "");
            s = s.replace(/\s+/g, "-");
            s = s.replace(/\-+/g, "-");
            s = this.trim_chars(s, "-");
            return s;
        },
        trim_chars: function (str, ch) {
            while (str.substr(0, 1) == ch)
                str = str.substr(1);
            var nrt = str.length;
            while (str.substr(nrt - 1, 1) == ch) {
                str = str.substr(0, nrt - 1);
                nrt = str.length;
            }
            return str;
        }
    }
}();
window.onload = BK.init;

function getQueryParams(qs) {
    qs = qs.split('+').join(' ');

    var params = {},
        tokens,
        re = /[?&]?([^=]+)=([^&]*)/g;

    while (tokens = re.exec(qs)) {
        params[decodeURIComponent(tokens[1])] = decodeURIComponent(tokens[2]);
    }

    return params;
}
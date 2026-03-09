<?php
/*
 * COED IA mediaimmagine - Snippet Homey homepage widget sopra slider
 * Data: 2026-02-26
 * Tutto via snippet: widget sopra slider (solo homepage), menu hamburger sopra widget e logo più grande (su tutte le pagine, solo smartphone).
 */

function homey_hpws_register_sidebars() {
    register_sidebar(array(
        'name'          => 'Homepage sopra slider - Area 1',
        'id'            => 'home-above-slider-1',
        'description'   => 'Contenuto mostrato in homepage sopra lo slider.',
        'before_widget' => '<div id="%1$s" class="widget %2$s home-above-slider-widget">',
        'after_widget'  => '</div>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ));
    register_sidebar(array(
        'name'          => 'Homepage sopra slider - Area 2',
        'id'            => 'home-above-slider-2',
        'description'   => 'Contenuto mostrato in homepage sopra lo slider.',
        'before_widget' => '<div id="%1$s" class="widget %2$s home-above-slider-widget">',
        'after_widget'  => '</div>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ));
}
add_action('widgets_init', 'homey_hpws_register_sidebars');

/* Su tutte le pagine (solo smartphone): menu sopra widget e logo più grande */
function homey_hpws_mobile_header_and_logo() {
    ?>
    <style id="homey-hpws-mobile-header-logo">
    @media (max-width: 767px) {
        .top-banner-wrap { z-index: 1 !important; }
        header, #header, .header, .site-header, .header-area, .header-wrap,
        .navbar, .navbar-header, .main-header, .nav-wrap, .nav-bar { z-index: 99999 !important; }
        .navbar-collapse, .collapse.navbar-collapse, .collapse, .nav-dropdown,
        .dropdown-menu, .off-canvas, .slideout-panel, .mobile-menu, .mobile-nav,
        [class*="navbar-collapse"], [class*="menu-overlay"], [class*="drawer"],
        .header .nav, .header-wrap .nav { position: relative !important; z-index: 99999 !important; }
        .custom-logo, .logo img, .site-logo img, .header-logo img, .navbar-brand img,
        .logo a img, .site-logo a img, header .logo img, .header-wrap .logo img,
        .navbar-header img, .brand-logo img, [class*="logo"] img, header img.custom-logo,
        header img:first-of-type, .header-wrap img:first-of-type {
            max-width: none !important; width: auto !important; height: 52px !important;
            min-height: 48px !important; object-fit: contain !important;
            transform: scale(1.55) !important; transform-origin: center center !important;
            display: block !important; margin-left: auto !important; margin-right: auto !important;
        }
        .logo, .site-logo, .header-logo, .navbar-brand, [class*="logo"],
        .logo a, .navbar-brand a, .site-logo a {
            max-width: 260px !important;
            padding-top: 12px !important; padding-bottom: 12px !important;
            display: flex !important; align-items: center !important; justify-content: center !important;
        }
        .navbar-header { padding-top: 12px !important; padding-bottom: 12px !important; }
    }
    </style>
    <script>
    (function(){
        var MENU_Z='99999', mq=window.matchMedia('(max-width: 767px)');
        function setZ(el){ if(el&&el.style){ var p=window.getComputedStyle(el).position; if(p==='static')el.style.position='relative'; el.style.zIndex=MENU_Z; }}
        function menuAbove(){ if(!mq.matches)return; var s='header,#header,.header,.site-header,.header-area,.header-wrap,.navbar,.navbar-collapse,.navbar-header,.collapse,.main-header,.nav-wrap,.mobile-nav,.dropdown-menu,.off-canvas,.nav-dropdown'; try{ document.querySelectorAll(s).forEach(setZ); }catch(e){}
            document.querySelectorAll('.in,.open,.show,.active').forEach(function(el){ if(el.closest('header')||el.closest('.navbar')||el.closest('[class*="nav"]')||el.closest('[class*="menu"]')) setZ(el); });
        }
        function logoBig(){ if(!mq.matches)return;
            var imgs=document.querySelectorAll('header img, .header-wrap img, .navbar-brand img');
            for(var i=0;i<imgs.length;i++){
                var img=imgs[i]; if(img.closest('.dropdown')) continue;
                if(img.classList.contains('custom-logo')||img.closest('[class*="logo"]')||(img.naturalWidth>60)||i===0){
                    img.style.setProperty('transform','scale(1.55)','important');
                    img.style.setProperty('transform-origin','center center','important');
                    img.style.setProperty('max-width','none','important');
                    img.style.setProperty('height','52px','important');
                    img.style.setProperty('width','auto','important');
                    break;
                }
            }
        }
        menuAbove(); logoBig();
        mq.addListener(function(){ menuAbove(); logoBig(); });
        setInterval(menuAbove,500);
        var obs=new MutationObserver(menuAbove); obs.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['class']});
        if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',function(){ logoBig(); });
        window.addEventListener('load',logoBig);
    })();
    </script>
    <?php
}
add_action('wp_footer', 'homey_hpws_mobile_header_and_logo', 4);

function homey_hpws_render_widgets_placeholder() {
    if (!is_front_page()) return;
    $sidebar_ids = array('home-above-slider-1', 'home-above-slider-2', 'custom-sidebar-1', 'custom-sidebar-2', 'custom_sidebar_1', 'custom_sidebar_2');
    $has_any = false;
    foreach ($sidebar_ids as $id) {
        if (is_active_sidebar($id)) { $has_any = true; break; }
    }
    if (!$has_any) return;
    ?>
    <div id="homey-hpws-above-slider" class="home-above-slider-wrap" style="display:none;">
        <div class="home-above-slider-inner" style="display:flex;flex-wrap:wrap;justify-content:center;">
            <?php foreach ($sidebar_ids as $id) : if (is_active_sidebar($id)) : ?>
                <div class="home-above-slider-area" style="flex:1;min-width:200px;"><?php dynamic_sidebar($id); ?></div>
            <?php endif; endforeach; ?>
        </div>
    </div>
    <style>
    .top-banner-wrap { position: relative !important; }
    #homey-hpws-above-slider {
        position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);
        width: 88%; max-width: 880px; z-index: 10;
        background: rgba(255, 255, 255, 0.82); border: 1px solid #fff; border-radius: 16px; padding: 28px 32px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        box-sizing: border-box;
    }
    #homey-hpws-above-slider .home-above-slider-inner { gap: 20px; }
    @media (max-width: 767px) {
        #homey-hpws-above-slider {
            top: 54%; padding: 20px 16px; width: 92%;
            background: rgba(255, 255, 255, 0.82); border: 1px solid #fff; box-shadow: 0 8px 32px rgba(0,0,0,0.08);
            overflow-x: auto; overflow-y: hidden; -webkit-overflow-scrolling: touch;
            scroll-snap-type: x mandatory; scroll-snap-stop: normal;
            z-index: 10;
        }
        #homey-hpws-above-slider .home-above-slider-inner {
            flex-direction: row; flex-wrap: nowrap; gap: 72px;
            width: max-content; min-width: 100%;
            padding-left: calc(46vw - 140px); padding-right: calc(46vw - 140px);
            box-sizing: content-box;
        }
        #homey-hpws-above-slider .home-above-slider-area {
            flex: 0 0 auto; width: 280px; min-width: 280px; max-width: 280px;
            scroll-snap-align: center; scroll-snap-stop: always;
        }
    }
    </style>
    <script>
    (function(){
        var wrap = document.getElementById('homey-hpws-above-slider');
        var target = document.querySelector('.top-banner-wrap');
        if (wrap && target) {
            target.style.position = 'relative';
            target.insertBefore(wrap, target.firstChild);
            wrap.style.display = 'block';
        }
    })();
    </script>
    <?php
}
add_action('wp_footer', 'homey_hpws_render_widgets_placeholder', 5);

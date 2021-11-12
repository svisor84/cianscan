from django_assets import Bundle, register

from jinja2.ext import Extension
from django_assets.env import get_env


class AssetsExtension(Extension):
    def __init__(self, environment):
        super(AssetsExtension, self).__init__(environment)
        environment.assets_environment = get_env()

# register('intro.shared_js', Bundle(
#   'assets/javascripts/yandex_metrika.js',
#   'assets/javascripts/yandex_metrika.bridge.js',

#   filters='jsmin', output='gen/intro.shared.js'
# ))

# register('mytc.shared_js', Bundle(
#   'bower_components/jquery/dist/jquery.min.js',
#   'plugins/ripple/ripple.min.js',
#   'plugins/jquery.cookie.js',

#   'build/global.bundle.js',

#   'assets/javascripts/application.js',
#   'assets/javascripts/ya_metr/ya_metr.lazy_exec.js',
#   'assets/javascripts/ya_metr/ya_metr.favorite_stores.js',

#   filters='jsmin', output='gen/mytc.shared.js'
# ))

# register('plugins_js', Bundle(
#   'plugins/underscore-min.js',
#   'plugins/jquery-ui/jquery-ui.min.js',
#   'plugins/jquery.visible.min.js',
#   'plugins/jquery.parseParams.js',
#   'bower_components/lz-string/libs/lz-string.min.js',
#   'bower_components/swiper/dist/js/swiper.min.js',
#   'bower_components/moment/min/moment.min.js',
#   'bower_components/moment/locale/ru.js',
#   'plugins/bootstrap/js/bootstrap.js',

#   filters='jsmin', output='gen/plugins.js'
# ))

# register('application_js', Bundle(
#   'assets/javascripts/module_transparent_img_loading.js',
#   'assets/javascripts/module_dynamic_resizable.js',
#   'assets/javascripts/module_like_btns_list.js',
#   'assets/javascripts/module_storage.js',

#   'assets/javascripts/jquery.ajax_form.min.js',
#   'assets/javascripts/scroll.js',

#   'assets/javascripts/page_scripts/custom_favorites_page.js',

#   'assets/javascripts/favorites.js',

#   'assets/javascripts/ya_metr/ya_metr.intro.js',
#   'assets/javascripts/ya_metr/ya_metr.menu.js',
#   'assets/javascripts/ya_metr/ya_metr.products.js',
#   'assets/javascripts/ya_metr/ya_metr.item.js',
#   'assets/javascripts/ya_metr/ya_metr.favorites.js',
#   'assets/javascripts/ya_metr/ya_metr.booking.js',
#   'assets/javascripts/ya_metr/ya_metr.application.js',
#   'assets/javascripts/fb_pixel.js',
#   'assets/_components/product-advantages/product-advantages.js',
#   'assets/_components/need-other-tc/need-other-tc.js',

#   filters='jsmin', output='gen/application.js'
# ))

# register('goodbye_css', Bundle(
# #   'plugins/bootstrap/css/bootstrap.css',
# #   'assets/stylesheets/bootstrap_and_overrides.css',

#   filters='cssmin', output='gen/goodbye.css'
# ))

# register('application_js', Bundle(
#   'assets/javascripts/module_transparent_img_loading.js',
#   'assets/javascripts/module_dynamic_resizable.js',
#   'assets/javascripts/module_like_btns_list.js',
#   'assets/javascripts/module_storage.js',

#   'assets/javascripts/jquery.ajax_form.min.js',
#   'assets/javascripts/scroll.js',

#   'assets/javascripts/page_scripts/custom_favorites_page.js',

#   'assets/javascripts/favorites.js',

#   'assets/javascripts/ya_metr/ya_metr.intro.js',
#   'assets/javascripts/ya_metr/ya_metr.menu.js',
#   'assets/javascripts/ya_metr/ya_metr.products.js',
#   'assets/javascripts/ya_metr/ya_metr.item.js',
#   'assets/javascripts/ya_metr/ya_metr.favorites.js',
#   'assets/javascripts/ya_metr/ya_metr.booking.js',
#   'assets/javascripts/ya_metr/ya_metr.application.js',
#   'assets/javascripts/fb_pixel.js',
#   'assets/_components/product-advantages/product-advantages.js',
#   'assets/_components/need-other-tc/need-other-tc.js',

#   filters='jsmin', output='gen/application.js'
# ))



# register('application_css', Bundle(
# # plugins
#   'plugins/jquery-ui/jquery-ui.css',
#   'bower_components/swiper/dist/css/swiper.min.css',

# # base
#   'assets/_base/atomic/atomic.css',
#   # 'assets/_base/atomic.css',

#   'assets/stylesheets/application.css',
#   'assets/stylesheets/common.css',
#   'assets/stylesheets/popovers.css',
#   'assets/stylesheets/popup-feedback.css',
#   'assets/stylesheets/popup-booking.css',
#   'assets/stylesheets/step_ones.css',
#   'assets/stylesheets/step_two.css',
#   'assets/stylesheets/products.css',
#   'assets/stylesheets/product.css',
#   'assets/stylesheets/product-card.css',
#   'assets/stylesheets/product-gallery.css',
#   'assets/stylesheets/product-filters.css',
#   'assets/stylesheets/purchases.css',
#   'assets/stylesheets/purchase_store_clusters.css',
#   'assets/stylesheets/where_can_buy_items.css',
#   'assets/stylesheets/where_can_buy_products.css',
#   'assets/stylesheets/stores.css',
#   'assets/stylesheets/badges.css',
#   'assets/stylesheets/look_filters.css',
#   'assets/stylesheets/favorites.css',

# # base page
#   'assets/_components/pageWithSideMenu/pageWithSideMenu.css',

# # common components
#   'assets/_components/grid/grid.css',
#   'assets/_components/infinityListSpinner/infinityListSpinner.css',
#   'assets/_components/sidemenu/sidemenu.css',
#   'assets/_components/sideMenuTabs/sideMenuTabs.css',
#   'assets/_components/dynamic-resizable-image/dynamic-resizable-image.css',
#   'assets/_components/product-advantages/product-advantages.css',

# # homepage
#   'assets/_components_homepage/homepage/homepage.css',
#   'assets/_components_homepage/homepage-header-text/homepage-header-text.css',
#   'assets/_components_homepage/homepage-menu/homepage-menu.css',
#   'assets/_components_homepage/homepage-tabs/homepage-tabs.css',
#   'assets/_components_homepage/home-week-banner/home-week-banner.css',
#   'assets/_components_homepage/salesBanners/salesBanners.css',
#   'assets/_components_homepage/which-clothes-do-you-find/which-clothes-do-you-find.css',
#   'assets/_components_homepage/setProductListBlock/setProductListBlock.css',
#   'assets/_components_homepage/moreSets/moreSets.css',

# # filters page
#   'assets/_components/filters-page/filters-page.css',
#   'assets/_components/filters-page-tabs/filters-page-tabs.css',
#   'assets/_components/filters-item/filters-item.css',

# # product-page
#   'assets/_components_product-page/product-page/product-page.css',
#   'assets/_components_product-page/product-availability-select/product-availability-select.css',
#   'assets/_components_product-page/product-availability-preview/product-availability-preview.css',
#   'assets/_components_product-page/product-availability-popup/product-availability-popup.css',
#   'assets/_components_product-page/end-of-product-page/end-of-product-page.css',
#   'assets/_components_product-page/product-snippet/product-snippet.css',
#   'assets/_components_product-page/product-description/product-description.css',
#   'assets/_components_product-page/product-sizes/product-sizes.css',
#   'assets/_components_product-page/product-stores/product-stores.css',
#   'assets/_components_product-page/product-like-button/product-like-button.css',
#   'assets/_components_product-page/hooray-swiper/hooray-swiper.css',
#   'assets/_components_product-page/hooray-item/hooray-item.css',
#   'assets/_components_product-page/hooray-actions/hooray-actions.css',
#   'assets/_components_product-page/another-day-actions/another-day-actions.css',
#   'assets/_components_product-page/productSwiper/productSwiper.css',

# # others
#   'assets/_components/product-card/product-card.css',
#   'assets/_components/product-cortage-col/product-cortage-col.css',

#   'assets/_components/my-storeclusters-panel/my-storeclusters-panel.css',
#   'assets/_components/filters/filters.css',

#   'assets/_components/productlist/productlist.css',
#   'assets/_components/productlist-notfound/productlist-notfound.css',
#   'assets/_components/horizontal-productlist/horizontal-productlist.css',
#   'assets/_components/recent-productlist/recent-productlist.css',

#   'assets/_components/bookingpage/bookingpage.css',
#   'assets/_components/booking-finish/booking-finish.css',

#   'assets/_components/modal-alert/modal-alert.css',
#   'assets/_components/card-spinner/card-spinner.css',
#   'assets/_components/need-other-tc/need-other-tc.css',

#   filters='cssmin', output='gen/application.css'
# ))

 # python manage.py assets build

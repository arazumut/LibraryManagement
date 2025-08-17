from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SITE_TITLE": _("Kütüphane Yönetimi"),
    "SITE_HEADER": _("Kütüphane Yönetimi"),
    "SITE_URL": "/admin",
    "SITE_ICON": None,  # Özel ikon tanımlaması için dosya yolu
    "SITE_SYMBOL": "book",  # Fontawesome sembolü
    "SHOW_TITLE": True,
    "SITE_TITLE_FORMAT": _("{site_title} Admin"),
    
    # Environment badge config
    "ENVIRONMENT": "development",
    "ENVIRONMENT_PALETTE": {
        "development": {
            "label": _("Development"),
            "classes": "danger",
        },
    },
    
    # Tema yapılandırması
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "items": [
            {
                "title": _("Kitaplar"),
                "icon": "book",
                "models": [
                    "books.book", 
                    "books.category", 
                    "books.readinggoal", 
                    "books.readingchallenge"
                ],
            },
            {
                "title": _("Kullanıcılar"),
                "icon": "user",
                "models": [
                    "accounts.user", 
                    "accounts.notification"
                ],
            },
            {
                "title": _("Kütüphaneler"),
                "icon": "building",
                "models": [
                    "libraries.library"
                ],
            },
            {
                "title": _("Ödünç İşlemleri"),
                "icon": "exchange",
                "models": [
                    "loans.loan"
                ],
            },
            {
                "title": _("API Yönetimi"),
                "icon": "code",
                "models": [
                    "api.apikey", 
                    "api.apirequest"
                ],
            },
            {
                "title": _("Sistem"),
                "icon": "gear",
                "models": [
                    "auth.group", 
                    "auth.permission"
                ],
            },
        ],
    },
    
    # Özel stil dosyaları
    "STYLES": [
        "/static/css/admin-custom.css",
    ],
    "SCRIPTS": [
        "/static/js/admin-custom.js",
    ],
    
    # Tema renkleri
    "COLORS": {
        "primary": {
            "50": "239, 246, 255",
            "100": "219, 234, 254",
            "200": "191, 219, 254",
            "300": "147, 197, 253",
            "400": "96, 165, 250",
            "500": "59, 130, 246",
            "600": "37, 99, 235",
            "700": "29, 78, 216",
            "800": "30, 64, 175",
            "900": "30, 58, 138",
        },
    },
    
    # Çeviriler için bayraklar
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "tr": "🇹🇷",
                "en": "🇬🇧",
            },
        },
    },
}

<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maison Trüvra - Marché des Pros</title>
    <!-- TailwindCSS will be injected by the build process from the main css file -->
    <link rel="stylesheet" href="/css/public.css">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@400;700&display=swap" rel="stylesheet">
</head>
<body class="bg-light-gray text-dark-brown font-sans">

    <!-- Header will be loaded from pro_common.js -->
    <div id="pro-header-placeholder"></div>

    <main class="container mx-auto px-6 py-12">
        <div class="text-center mb-12">
            <h1 class="text-5xl font-bold font-serif text-truffle-burgundy mb-2" data-i18n="marchedespros.title">Marché des Pros</h1>
            <p class="text-lg text-gray-600" data-i18n="marchedespros.subtitle">Votre source exclusive pour les meilleurs produits à base de truffe.</p>
        </div>

        <!-- Vue App for B2B Shop will be mounted here -->
        <div id="b2b-shop">
            <div class="text-center p-8">
                <p class="text-lg text-dark-brown">Chargement de la boutique...</p>
            </div>
        </div>
    </main>

    <!-- Footer will be loaded from pro_common.js -->
    <div id="pro-footer-placeholder"></div>

    <script type="module" src="/js/i18n.js"></script>
    <script type="module" src="/pro/js/pro_common.js"></script>
    <script type="module" src="/pro/js/b2b-shop-loader.js"></script>

</body>
</html>

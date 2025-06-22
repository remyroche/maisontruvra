<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Assuming Tailwind CSS is linked -->
</head>
<body>

<footer class="bg-gray-700 text-white mt-12">
    <div class="container mx-auto p-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <!-- About Section -->
            <div>
                <h3 class="text-lg font-bold mb-4">Maison Truvra</h3>
                <p class="text-gray-400">Premium products for dedicated professionals. Quality and trust, delivered.</p>
            </div>

            <!-- Quick Links -->
            <div>
                <h3 class="text-lg font-bold mb-4">Quick Links</h3>
                <ul>
                    <li><a href="/pro/marchedespros.html" class="hover:text-gray-300">Pro Market</a></li>
                    <li><a href="/pro/invoices-pro.html" class="hover:text-gray-300">My Invoices</a></li>
                    <li><a href="/pro/profile.html" class="hover:text-gray-300">My Profile</a></li>
                </ul>
            </div>

            <!-- Newsletter Subscription -->
            <div>
                <h3 class="text-lg font-bold mb-4">Subscribe to our Newsletter</h3>
                <p class="text-gray-400 mb-4">Get the latest news, offers, and insights for professionals.</p>
                <form id="pro-newsletter-form">
                    <div class="flex">
                        <input type="email" id="pro-newsletter-email" placeholder="Your email address" class="w-full px-4 py-2 text-gray-800 rounded-l-md focus:outline-none" required>
                        <button type="submit" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-r-md">Subscribe</button>
                    </div>
                </form>
                <p id="pro-newsletter-feedback" class="mt-2 text-sm"></p>
            </div>
        </div>
        <div class="text-center text-gray-500 border-t border-gray-600 pt-4 mt-8">
            &copy; 2024 Maison Truvra. All Rights Reserved.
        </div>
    </div>
</footer>

<!-- This script will handle the newsletter form submission -->
<script type="module" src="/pro/js/pro_footer.js"></script>

</body>
</html>

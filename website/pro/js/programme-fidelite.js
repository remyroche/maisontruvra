// website/source/pro/js/programme-fidelite.js
document.addEventListener('DOMContentLoaded', () => {
    const api = new API();
    const tiersContainer = document.getElementById('tiers-cards-container');
    const ambassadorContainer = document.getElementById('ambassador-section');

    const renderTiers = (tiers) => {
        if (!tiersContainer) return;
        
        const tierConfig = {
            collaborateur: {
                title: 'Collaborateur',
                description: 'Le point de départ de l\'innovation.',
                benefits: [
                    `Tarification professionnelle préférentielle (jusqu'à -${tiers.collaborateur?.discount_percentage || 50}%)`,
                    'Accès complet au portail de commande B2B',
                    'Support technique et culinaire dédié'
                ],
                style: 'border-gray-300'
            },
            partenaire: {
                title: 'Partenaire',
                description: 'Concevoir de nouvelles structures de saveurs.',
                benefits: [
                    'Tous les bénéfices de Collaborateur',
                    `Remise additionnelle de ${tiers.partenaire?.discount_percentage || '5-10'}%`,
                    'Allocation prioritaire des récoltes `Origine`',
                    'Accès anticipé aux collections de l\'Atelier'
                ],
                style: 'border-brand-gold transform md:scale-105 shadow-xl',
                titleColor: 'text-brand-burgundy'
            },
            associé: {
                title: 'Associé',
                description: 'Définir l\'avenir de la gastronomie.',
                benefits: [
                    'Tous les bénéfices d\'Architecte',
                    `Remise additionnelle de ${tiers.associe?.discount_percentage || 15}%`,
                    'Droit de premier refus sur l\'Avant-Garde',
                    'Invitation à la table ronde R&D annuelle',
                    'Potentiel de collaboration directe avec le labo'
                ],
                style: 'border-gray-300'
            }
        };

        let html = '';
        ['collaborateur', 'partenaire', 'associe'].forEach(key => {
            const config = tierConfig[key];
            if(config) {
                 html += `
                    <div class="tier-card bg-white p-8 rounded-lg shadow-lg border-t-4 ${config.style}">
                        <h3 class="font-serif text-2xl ${config.titleColor || 'text-brand-dark-gray'} mb-2">${config.title}</h3>
                        <p class="font-sans text-brand-dark-gray mb-6 italic h-12">${config.description}</p>
                        <ul class="text-left space-y-3 font-sans text-brand-dark-gray">
                            ${config.benefits.map(benefit => `<li>${benefit}</li>`).join('')}
                        </ul>
                    </div>`;
            }
        });
        tiersContainer.innerHTML = html;

        if (ambassadorContainer && tiers.ambassadeur) {
            ambassadorContainer.innerHTML = `
                <div class="max-w-4xl mx-auto text-center p-10 border-2 border-brand-gold rounded-xl bg-brand-cream">
                    <h2 class="font-serif text-3xl text-brand-gold mb-2">Ambassadeur Maison Trüvra</h2>
                    <p class="font-sans text-brand-dark-gray mb-6 italic">Une distinction sur invitation uniquement.</p>
                    <p class="font-sans text-lg text-brand-dark-gray leading-relaxed">
                        Le titre d'Ambassadeur est réservé aux chefs étoilés Michelin. Ils bénéficient d'un accès sans précédent à notre laboratoire, d'une remise de ${tiers.ambassadeur.discount_percentage}%, et de tous les avantages du niveau Partenaire Visionnaire, en reconnaissance de leur rôle essentiel dans la définition de l'avenir de la gastronomie.
                    </p>
                </div>`;
        }
    };

    const fetchTiers = async () => {
        try {
            // This is the PUBLIC API endpoint
            const tiersData = await api.get('/api/b2b/loyalty/tiers'); 
            // The API should return an object with keys: collaborateur, architecte, etc.
            renderTiers(tiersData);
        } catch (error) {
            console.error('Failed to load B2B tier information:', error);
            if (tiersContainer) {
                tiersContainer.innerHTML = '<p class="text-center text-red-600">Could not load loyalty program details at this time.</p>';
            }
        }
    };

    fetchTiers();
});


document.addEventListener('DOMContentLoaded', () => {
    const api = new ProAPI();

    // --- Dashboard Elements ---
    const loadingEl = document.getElementById('dashboard-loading');
    const contentEl = document.getElementById('dashboard-content');
    const currentTierNameEl = document.getElementById('current-tier-name');
    const progressBarEl = document.getElementById('tier-progress-bar');
    const currentPointsEl = document.getElementById('current-points');
    const nextTierPointsEl = document.getElementById('next-tier-points');
    const totalPointsDisplayEl = document.getElementById('total-points-display');
    const tiersContainer = document.getElementById('tiers-cards-container');
    const referralCodeEl = document.getElementById('referral-code');
    const referralEarningsListEl = document.getElementById('referral-earnings-list');

    const tierConfig = {
        collaborateur: {
            title: 'Collaborateur',
            benefits: [
                'Tarification professionnelle de base',
                'Accès complet au portail de commande B2B',
                'Support technique et culinaire dédié'
            ]
        },
        partenaire: {
            title: 'Partenaire',
            benefits: [
                'Tous les bénéfices de Collaborateur',
                'Remise additionnelle sur les produits',
                'Allocation prioritaire des récoltes `Origine`',
                'Accès anticipé aux collections de l\'Atelier'
            ]
        },
        associe: {
            title: 'Associé',
            benefits: [
                'Tous les bénéfices de Partenaire',
                'Remise additionnelle supérieure',
                'Droit de premier refus sur l\'Avant-Garde',
                'Invitation à la table ronde R&D annuelle',
                'Potentiel de collaboration directe avec le labo'
            ]
        }
    };

    function renderDashboard(data) {
        const { dashboard, recent_referral_earnings, tier_definitions } = data;
        const currentTier = dashboard.current_tier;
        const tiers = tier_definitions.sort((a,b) => a.points_threshold - b.points_threshold);
        
        // --- Populate Top Dashboard ---
        totalPointsDisplayEl.textContent = dashboard.current_points.toLocaleString('fr-FR');
        currentPointsEl.textContent = dashboard.current_points.toLocaleString('fr-FR');
        if (currentTier) {
            currentTierNameEl.textContent = currentTier.display_name;
        }

        // --- Progress Bar Logic ---
        const currentTierIndex = tiers.findIndex(t => t.id === currentTier.id);
        let nextTier = null;
        if(currentTierIndex < tiers.length - 1){
            nextTier = tiers[currentTierIndex + 1];
        }

        if (nextTier) {
            nextTierPointsEl.textContent = nextTier.points_threshold.toLocaleString('fr-FR');
            const pointsForCurrentLevel = dashboard.current_points - currentTier.points_threshold;
            const pointsNeededForNextLevel = nextTier.points_threshold - currentTier.points_threshold;
            const progressPercentage = Math.min(100, (pointsForCurrentLevel / pointsNeededForNextLevel) * 100);
            progressBarEl.style.width = `${progressPercentage}%`;
        } else {
            // Max tier reached
            nextTierPointsEl.parentElement.innerHTML = 'Niveau maximum atteint';
            progressBarEl.style.width = '100%';
        }

        // --- Render Tier Cards ---
        tiersContainer.innerHTML = tiers.map(tier => {
            const config = tierConfig[tier.key_name];
            const isActive = currentTier.id === tier.id;
            const isAchieved = dashboard.current_points >= tier.points_threshold;
            
            const cardStyle = isActive ? 'border-brand-gold shadow-xl transform md:scale-105' : 'border-gray-200';
            const titleColor = isActive ? 'text-brand-burgundy' : 'text-brand-dark-gray';
            const opacity = isAchieved ? 'opacity-100' : 'opacity-50';

            return `
                <div class="tier-card bg-white p-6 rounded-lg shadow-lg border-t-4 ${cardStyle} ${opacity} transition-all duration-300">
                    <div class="flex justify-between items-center">
                         <h4 class="font-serif text-xl ${titleColor} mb-2">${tier.display_name}</h4>
                         ${isAchieved ? '<span class="bg-green-100 text-green-800 text-xs font-bold px-2.5 py-1 rounded-full">Atteint</span>' : ''}
                    </div>
                    <p class="font-sans text-brand-dark-gray mb-4 text-left text-sm">Dès ${tier.points_threshold.toLocaleString('fr-FR')} points</p>
                    <ul class="text-left space-y-2 font-sans text-brand-dark-gray text-sm">
                        ${config ? config.benefits.map(b => `<li>${b}</li>`).join('') : ''}
                    </ul>
                </div>
            `;
        }).join('');

        // --- Populate Referral Section ---
        referralCodeEl.textContent = dashboard.referral_code || 'Non disponible';
        if (recent_referral_earnings && recent_referral_earnings.length > 0) {
            referralEarningsListEl.innerHTML = recent_referral_earnings.map(e => `
                <li class="flex justify-between items-center text-sm border-b border-brand-light-gray py-2">
                    <span>De la commande #${e.triggering_order_id}</span>
                    <span class="font-bold text-green-600">+${e.points_awarded.toFixed(2)} pts</span>
                </li>
            `).join('');
        } else {
            referralEarningsListEl.innerHTML = '<li class="text-sm text-brand-dark-gray italic">Aucun gain de parrainage récent.</li>';
        }

        // Show content
        loadingEl.style.display = 'none';
        contentEl.classList.remove('hidden');
    }

    const loadDashboardData = async () => {
        try {
            const data = await api.get('/api/b2b/loyalty/dashboard');
            renderDashboard(data);
        } catch (error) {
            console.error('Failed to load loyalty dashboard:', error);
            loadingEl.innerHTML = '<p class="text-red-600 text-center">Erreur lors du chargement de vos données.</p>';
        }
    };

    loadDashboardData();
});


import { TestHelpers } from './test-helpers';

export interface TestProduct {
  id: string;
  name: string;
  price: number;
  category: string;
  sku: string;
  inStock: boolean;
}

export interface TestUser {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phone?: string;
}

export interface TestB2BUser extends TestUser {
  companyName: string;
  siret: string;
  vatNumber?: string;
}

export interface TestAddress {
  line1: string;
  line2?: string;
  city: string;
  state?: string;
  postalCode: string;
  country: string;
}

export class TestDataGenerator {
  static generateUser(): TestUser {
    return {
      email: TestHelpers.generateRandomEmail(),
      password: 'TestPass123!',
      firstName: this.getRandomFirstName(),
      lastName: this.getRandomLastName(),
      phone: TestHelpers.generateRandomPhone()
    };
  }

  static generateB2BUser(): TestB2BUser {
    const baseUser = this.generateUser();
    return {
      ...baseUser,
      companyName: this.getRandomCompanyName(),
      siret: TestHelpers.generateRandomSiret().toString(),
      vatNumber: `FR${Math.floor(Math.random() * 90000000000) + 10000000000}`
    };
  }

  static generateAddress(): TestAddress {
    const addresses = [
      {
        line1: '123 Rue de la Paix',
        city: 'Paris',
        postalCode: '75001',
        country: 'France'
      },
      {
        line1: '456 Avenue des Champs-Élysées',
        city: 'Paris',
        postalCode: '75008',
        country: 'France'
      },
      {
        line1: '789 Boulevard Saint-Germain',
        city: 'Paris',
        postalCode: '75007',
        country: 'France'
      },
      {
        line1: '321 Rue du Faubourg Saint-Honoré',
        city: 'Paris',
        postalCode: '75001',
        country: 'France'
      }
    ];

    return addresses[Math.floor(Math.random() * addresses.length)];
  }

  static generateProduct(): TestProduct {
    const products = [
      {
        name: 'Thé Earl Grey Premium',
        price: 24.99,
        category: 'Thés noirs',
        sku: 'TEA-EG-001'
      },
      {
        name: 'Infusion Camomille Bio',
        price: 18.50,
        category: 'Infusions',
        sku: 'INF-CAM-002'
      },
      {
        name: 'Thé Vert Sencha',
        price: 32.00,
        category: 'Thés verts',
        sku: 'TEA-SEN-003'
      },
      {
        name: 'Rooibos Vanille',
        price: 21.75,
        category: 'Rooibos',
        sku: 'ROO-VAN-004'
      },
      {
        name: 'Théière en Porcelaine',
        price: 89.99,
        category: 'Accessoires',
        sku: 'ACC-TEA-005'
      }
    ];

    const randomProduct = products[Math.floor(Math.random() * products.length)];
    return {
      id: TestHelpers.generateRandomString(8),
      ...randomProduct,
      inStock: Math.random() > 0.1 // 90% chance of being in stock
    };
  }

  static generateMultipleProducts(count: number): TestProduct[] {
    const products: TestProduct[] = [];
    for (let i = 0; i < count; i++) {
      products.push(this.generateProduct());
    }
    return products;
  }

  static generateOrderData() {
    return {
      products: this.generateMultipleProducts(Math.floor(Math.random() * 3) + 1),
      shippingAddress: this.generateAddress(),
      billingAddress: this.generateAddress(),
      paymentMethod: 'card',
      deliveryMethod: 'standard'
    };
  }

  static generateSearchQueries(): string[] {
    return [
      'thé',
      'earl grey',
      'bio',
      'camomille',
      'vert',
      'théière',
      'infusion',
      'rooibos'
    ];
  }

  static generatePromoCode(): string {
    const codes = [
      'WELCOME10',
      'SUMMER20',
      'BIENVENUE',
      'FIRST15',
      'LOYALTY5'
    ];
    return codes[Math.floor(Math.random() * codes.length)];
  }

  static generateCreditCard() {
    return {
      number: '4111111111111111', // Test Visa card
      expiry: '12/25',
      cvv: '123',
      name: 'Test User'
    };
  }

  static generateReviewData() {
    const reviews = [
      {
        rating: 5,
        title: 'Excellent produit',
        content: 'Je recommande vivement ce produit. La qualité est au rendez-vous.'
      },
      {
        rating: 4,
        title: 'Très satisfait',
        content: 'Bon produit, livraison rapide. Quelques petits détails à améliorer.'
      },
      {
        rating: 5,
        title: 'Parfait',
        content: 'Rien à redire, exactement ce que j\'attendais. Merci Maison Trüvra!'
      },
      {
        rating: 3,
        title: 'Correct',
        content: 'Le produit est correct mais sans plus. Prix un peu élevé.'
      }
    ];

    return reviews[Math.floor(Math.random() * reviews.length)];
  }

  static generateNewsletterEmail(): string {
    return TestHelpers.generateRandomEmail();
  }

  static generateBlogComment() {
    const comments = [
      'Article très intéressant, merci pour ces informations !',
      'J\'ai appris beaucoup de choses, continuez ainsi.',
      'Excellent contenu, hâte de lire le prochain article.',
      'Très instructif, je vais essayer vos conseils.'
    ];

    return {
      content: comments[Math.floor(Math.random() * comments.length)],
      author: this.getRandomFirstName()
    };
  }

  private static getRandomFirstName(): string {
    const names = [
      'Jean', 'Marie', 'Pierre', 'Anne', 'Michel', 'Françoise',
      'Philippe', 'Monique', 'Alain', 'Catherine', 'Bernard', 'Martine',
      'Robert', 'Sylvie', 'Henri', 'Brigitte', 'Daniel', 'Nicole',
      'Jacques', 'Claudine', 'Gérard', 'Christine', 'André', 'Isabelle'
    ];
    return names[Math.floor(Math.random() * names.length)];
  }

  private static getRandomLastName(): string {
    const names = [
      'Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert', 'Richard',
      'Petit', 'Durand', 'Leroy', 'Moreau', 'Simon', 'Laurent',
      'Lefebvre', 'Michel', 'Garcia', 'Roux', 'David', 'Bertrand',
      'Morel', 'Fournier', 'Girard', 'Bonnet', 'Dupont', 'Lambert'
    ];
    return names[Math.floor(Math.random() * names.length)];
  }

  private static getRandomCompanyName(): string {
    const prefixes = ['Société', 'Entreprise', 'Groupe', 'Établissement'];
    const suffixes = ['SARL', 'SAS', 'SA', 'EURL', 'SNC'];
    const businessTypes = [
      'Distribution', 'Commerce', 'Services', 'Consulting', 'Import-Export',
      'Restauration', 'Hôtellerie', 'Retail', 'Gestion', 'Développement'
    ];

    const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
    const businessType = businessTypes[Math.floor(Math.random() * businessTypes.length)];
    const suffix = suffixes[Math.floor(Math.random() * suffixes.length)];
    const randomName = this.getRandomLastName();

    return `${prefix} ${randomName} ${businessType} ${suffix}`;
  }

  static generateWishlistData() {
    return {
      products: this.generateMultipleProducts(Math.floor(Math.random() * 5) + 1)
    };
  }

  static generateB2BQuote() {
    return {
      products: this.generateMultipleProducts(Math.floor(Math.random() * 10) + 5),
      quantity: Math.floor(Math.random() * 50) + 10,
      message: 'Demande de devis pour commande en gros. Merci de nous faire parvenir vos meilleurs tarifs.',
      deliveryDate: new Date(Date.now() + Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000)
    };
  }
}

export const TEST_CONSTANTS = {
  TIMEOUTS: {
    SHORT: 5000,
    MEDIUM: 10000,
    LONG: 30000
  },
  RETRY_ATTEMPTS: 3,
  DEFAULT_PASSWORD: 'TestPass123!',
  ADMIN_PASSWORD: 'AdminPass123!',
  API_ENDPOINTS: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    PRODUCTS: '/api/products',
    CART: '/api/cart',
    ORDERS: '/api/orders',
    USERS: '/api/admin/users',
    B2B_DASHBOARD: '/api/b2b/dashboard'
  },
  SELECTORS: {
    LOADING: '[data-testid="loading-spinner"]',
    ERROR_MESSAGE: '[data-testid="error-message"]',
    SUCCESS_MESSAGE: '[data-testid="success-message"]',
    MODAL: '[data-testid="modal"]',
    FORM_VALIDATION: '.error-message'
  }
};
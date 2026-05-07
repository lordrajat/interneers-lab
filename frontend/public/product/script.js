const API_URL = "/products/";

const state = {
  products: [],
  expandedProductId: null,
};

const dummyProducts = [
  {
    id: "dummy-1",
    name: "Nebula Wireless Mouse",
    description: "Ergonomic wireless mouse with silent clicks and adjustable DPI.",
    category: { title: "Accessories" },
    price: 24.99,
    brand: "OrbitGear",
    quantity: 42,
  },
  {
    id: "dummy-2",
    name: "Aero 27 Monitor",
    description: "27-inch IPS monitor with vibrant color and slim bezels.",
    category: { title: "Displays" },
    price: 219.5,
    brand: "ViewEdge",
    quantity: 16,
  },
  {
    id: "dummy-3",
    name: "Pulse Mechanical Keyboard",
    description: "Compact mechanical keyboard with tactile switches and backlight.",
    category: { title: "Accessories" },
    price: 89.0,
    brand: "TypeLab",
    quantity: 30,
  },
];

const elements = {
  category: document.getElementById("productCategory"),
  name: document.getElementById("productName"),
  description: document.getElementById("productDescription"),
  price: document.getElementById("productPrice"),
  brand: document.getElementById("productBrand"),
  quantity: document.getElementById("productQuantity"),
  list: document.getElementById("productList"),
  statusText: document.getElementById("statusText"),
  refreshBtn: document.getElementById("refreshBtn"),
};

function setStatus(message) {
  elements.statusText.textContent = message;
}

function formatPrice(value) {
  const num = Number(value);
  if (Number.isNaN(num)) {
    return "$0.00";
  }
  return `$${num.toFixed(2)}`;
}

function updateFeaturedTile(product) {
  if (!product) {
    elements.category.textContent = "Category";
    elements.name.textContent = "No products available";
    elements.description.textContent = "Create products to see live API data here.";
    elements.price.textContent = "$0.00";
    elements.brand.textContent = "Brand";
    elements.quantity.textContent = "Qty: 0";
    return;
  }

  elements.category.textContent = product.category?.title || "Uncategorized";
  elements.name.textContent = product.name || "Unnamed product";
  elements.description.textContent = product.description || "No description";
  elements.price.textContent = formatPrice(product.price);
  elements.brand.textContent = product.brand || "Unknown brand";
  elements.quantity.textContent = `Qty: ${product.quantity ?? 0}`;
}

function renderProductList(products) {
  if (!products.length) {
    elements.list.innerHTML = '<div class="empty-state">No products returned by API.</div>';
    return;
  }

  const cards = products
    .map(
      (product) => `
      <article class="product-card ${state.expandedProductId === product.id ? "expanded" : ""}" data-product-id="${product.id}">
        <button type="button" class="product-card-button" data-product-id="${product.id}">
          <div>
            <span class="chip">${product.category?.title || "Uncategorized"}</span>
            <h4>${product.name || "Unnamed product"}</h4>
          </div>
          <strong>${formatPrice(product.price)}</strong>
        </button>
        <div class="product-detail ${state.expandedProductId === product.id ? "open" : ""}">
          <p>${product.description || "No description"}</p>
          <p>${product.brand || "Unknown brand"} | Qty: ${product.quantity ?? 0}</p>
        </div>
      </article>
    `
    )
    .join("");

  elements.list.innerHTML = cards;
}

function toggleProductDetails(productId) {
  state.expandedProductId =
    state.expandedProductId === productId ? null : productId;

  const selectedProduct = state.products.find((product) => product.id === productId);
  if (selectedProduct) {
    updateFeaturedTile(selectedProduct);
  }

  renderProductList(state.products);
}

async function fetchProducts() {
  setStatus("Loading...");

  try {
    const response = await fetch(API_URL);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const json = await response.json();
    console.log("Incoming API data:", json);

    state.products = Array.isArray(json.products) ? json.products : [];
    state.expandedProductId = null;
    updateFeaturedTile(state.products[0]);
    renderProductList(state.products);
    setStatus(`Loaded ${state.products.length} product(s). Check console for raw API data.`);
  } catch (error) {
    console.error("Product API call failed:", error);
    state.products = dummyProducts;
    state.expandedProductId = null;
    updateFeaturedTile(state.products[0]);
    renderProductList(state.products);
    setStatus("API unavailable. Showing dummy products for practice.");
  }
}

elements.refreshBtn.addEventListener("click", fetchProducts);
elements.list.addEventListener("click", (event) => {
  const target = event.target.closest("[data-product-id]");
  if (!target) {
    return;
  }

  toggleProductDetails(target.getAttribute("data-product-id"));
});
fetchProducts();

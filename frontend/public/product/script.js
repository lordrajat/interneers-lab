const API_URL = "/products/";

const state = {
  products: [],
};

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
      <article class="product-card">
        <span class="chip">${product.category?.title || "Uncategorized"}</span>
        <h4>${product.name || "Unnamed product"}</h4>
        <p>${product.description || "No description"}</p>
        <p><strong>${formatPrice(product.price)}</strong></p>
        <p>${product.brand || "Unknown brand"} | Qty: ${product.quantity ?? 0}</p>
      </article>
    `
    )
    .join("");

  elements.list.innerHTML = cards;
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
    updateFeaturedTile(state.products[0]);
    renderProductList(state.products);
    setStatus(`Loaded ${state.products.length} product(s). Check console for raw API data.`);
  } catch (error) {
    console.error("Product API call failed:", error);
    updateFeaturedTile(null);
    renderProductList([]);
    setStatus("Failed to load products. Ensure backend is running on port 8001.");
  }
}

elements.refreshBtn.addEventListener("click", fetchProducts);
fetchProducts();

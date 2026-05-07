import React from "react";
import "./App.scss";

type Product = {
  id: number;
  name: string;
  category: string;
  price: number;
  brand: string;
  quantity: number;
  description: string;
};

type ProductCardProps = {
  product: Product;
  isExpanded: boolean;
  onToggle: (id: number) => void;
};

const dummyProducts: Product[] = [
  {
    id: 1,
    name: "Nebula Wireless Mouse",
    category: "Accessories",
    price: 24.99,
    brand: "OrbitGear",
    quantity: 42,
    description:
      "Ergonomic wireless mouse with silent clicks and adjustable DPI.",
  },
  {
    id: 2,
    name: "Aero 27 Monitor",
    category: "Displays",
    price: 219.5,
    brand: "ViewEdge",
    quantity: 16,
    description: "27-inch IPS monitor with vibrant color and slim bezels.",
  },
  {
    id: 3,
    name: "Pulse Mechanical Keyboard",
    category: "Accessories",
    price: 89.0,
    brand: "TypeLab",
    quantity: 30,
    description:
      "Compact mechanical keyboard with tactile switches and backlight.",
  },
];

function ProductCard({ product, isExpanded, onToggle }: ProductCardProps) {
  return (
    <article className={`product-card ${isExpanded ? "expanded" : ""}`}>
      <button
        type="button"
        className="product-summary"
        onClick={() => onToggle(product.id)}
      >
        <div>
          <p className="chip">{product.category}</p>
          <h3>{product.name}</h3>
        </div>
        <strong>${product.price.toFixed(2)}</strong>
      </button>

      {isExpanded ? (
        <div className="product-details">
          <p>{product.description}</p>
          <p>Brand: {product.brand}</p>
          <p>Quantity: {product.quantity}</p>
        </div>
      ) : null}
    </article>
  );
}

type ProductListProps = {
  products: Product[];
};

function ProductList({ products }: ProductListProps) {
  const [expandedId, setExpandedId] = React.useState<number | null>(null);

  const handleToggle = (id: number) => {
    setExpandedId((current) => (current === id ? null : id));
  };

  return (
    <section className="product-list-section">
      <h2>Product List</h2>
      <p className="subtitle">
        Click a product to expand details. Data below is dummy data for Week 7.
      </p>

      <div className="product-list">
        {products.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            isExpanded={expandedId === product.id}
            onToggle={handleToggle}
          />
        ))}
      </div>
    </section>
  );
}

function App() {
  return (
    <div className="app">
      <header className="topbar">
        <h1>Interneers Product Lab</h1>
        <nav>
          <a href="#products">Products</a>
          <a href="#about">About</a>
          <a href="#help">Help</a>
        </nav>
      </header>

      <main className="content">
        <section className="hero">
          <p>Week 7 React + TypeScript</p>
          <h2>Product Dashboard</h2>
        </section>

        <div id="products">
          <ProductList products={dummyProducts} />
        </div>
      </main>
    </div>
  );
}

export default App;

const products = [
  {
    name: "Short Pesquero Invisible Dubai",
    price: "$105,000.00",
    category: "short",
    image: "https://fajaskayros.com/wp-content/uploads/2024/06/shortdubaiinvisibleppal-500x500.jpg",
    url: "https://fajaskayros.com/producto/short-pesquero-invisible-dubai/",
  },
  {
    name: "Short Invisible Venecia",
    price: "$99,900.00",
    category: "short",
    image: "https://fajaskayros.com/wp-content/uploads/2024/06/shortveneciainvisibleppal-500x500.jpg",
    url: "https://fajaskayros.com/producto/short-invisible-venecia/",
  },
  {
    name: "Panty Short Cachetero Nicol",
    price: "$75,000.00",
    category: "short",
    image: "https://fajaskayros.com/wp-content/uploads/2024/06/shortnicollppal-500x500.jpg",
    url: "https://fajaskayros.com/producto/panty-short-cachetero-nicol/",
  },
  {
    name: "Short Levanta Cola Paris",
    price: "$95,000.00",
    category: "short",
    image: "https://fajaskayros.com/wp-content/uploads/2024/06/shortparisppal-500x500.jpg",
    url: "https://fajaskayros.com/producto/short-levanta-cola-paris/",
  },
  {
    name: "Short Levanta Cola Invisible Adonai",
    price: "$95,000.00",
    category: "short",
    image: "https://fajaskayros.com/wp-content/uploads/2024/06/shortadonaiinvisibleppal-500x500.jpg",
    url: "https://fajaskayros.com/producto/short-levanta-cola-invisible-adonai/",
  },
  {
    name: "Short Levanta Cola Mónaco",
    price: "$90,000.00",
    category: "short",
    image: "https://fajaskayros.com/wp-content/uploads/2024/06/pantyshortmonacobeigeppal-500x500.jpg",
    url: "https://fajaskayros.com/producto/short-levanta-cola-monaco/",
  },
  {
    name: "Cintura de Sirena Dayana 13 varillas",
    price: "$139,900.00",
    category: "fajas",
    image: "https://fajaskayros.com/wp-content/uploads/2024/02/Dayana-4-1.png",
    url: "https://fajaskayros.com/producto/cintura-de-sirena-dayana-13-varillas/",
  },
  {
    name: "Cintura de Sirena Dayana 15 varillas",
    price: "$149,900.00",
    category: "fajas",
    image: "https://fajaskayros.com/wp-content/uploads/2024/02/Dayana-4-1.png",
    url: "https://fajaskayros.com/producto/cintura-de-sirena-dayana-15-varillas/",
  },
  {
    name: "Leggins Faja con Cinturilla Látex",
    price: "$120,000.00",
    category: "latex",
    image: "https://fajaskayros.com/wp-content/uploads/2026/03/laterales-cuadrados-500x500.png",
    url: "https://fajaskayros.com/producto/leggins-faja-con-cinturilla-latex/",
  },
  {
    name: "Jean Push Up Dama Faja",
    price: "$129,900.00",
    category: "fajas",
    image: "https://fajaskayros.com/wp-content/uploads/2025/08/Cinturilla-super-fit-detalle-broche-scaled.png",
    url: "https://fajaskayros.com/producto/jean-push-up-dama-faja/",
  },
  {
    name: "Short Levanta Cola Charlotte",
    price: "$85,000.00",
    category: "short",
    image: "https://fajaskayros.com/wp-content/uploads/2024/06/shortparisppal-500x500.jpg",
    url: "https://fajaskayros.com/producto/short-levanta-cola-charlotte/",
  },
  {
    name: "Faja Pescador Tannia",
    price: "$185,000.00",
    category: "fajas",
    image: "https://fajaskayros.com/wp-content/uploads/2025/08/Cinturilla-super-fit-detalle-broche-scaled.png",
    url: "https://fajaskayros.com/producto/faja-pescador-tannia/",
  },
];

const productGrid = document.querySelector("#product-grid");
const filters = document.querySelectorAll(".filter");
const menuToggle = document.querySelector(".menu-toggle");
const navLinks = document.querySelector("#nav-links");

function renderProducts(filter = "all") {
  const visibleProducts =
    filter === "all" ? products : products.filter((product) => product.category === filter);

  productGrid.innerHTML = visibleProducts
    .map(
      (product) => `
        <article class="product-card" data-category="${product.category}">
          <a class="product-image" href="${product.url}" target="_blank" rel="noopener">
            <img src="${product.image}" alt="${product.name}" loading="lazy" />
          </a>
          <div class="product-body">
            <span class="tag">${product.category}</span>
            <h3>${product.name}</h3>
            <div class="product-meta">
              <span class="price">${product.price}</span>
              <a class="button secondary" href="${product.url}" target="_blank" rel="noopener">
                Ver
              </a>
            </div>
          </div>
        </article>
      `
    )
    .join("");
}

filters.forEach((button) => {
  button.addEventListener("click", () => {
    filters.forEach((filter) => filter.classList.remove("active"));
    button.classList.add("active");
    renderProducts(button.dataset.filter);
  });
});

menuToggle.addEventListener("click", () => {
  const isOpen = navLinks.classList.toggle("open");
  menuToggle.setAttribute("aria-expanded", String(isOpen));
});

renderProducts();

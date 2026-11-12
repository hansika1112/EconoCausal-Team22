import { useEffect, useMemo, useState } from "react";
import {
  LayoutDashboard, Database, TrendingUp, BrainCircuit,
  ChartNoAxesCombined, Settings, Bell, Search, Menu,
  RefreshCw, DollarSign, ShoppingCart, Activity,
  ChevronDown, CircleHelp, Target, X,
  FileBarChart, AlertTriangle
} from "lucide-react";
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, BarChart, Bar, PieChart, Pie, Cell
} from "recharts";
import "./App.css";

const API = "http://127.0.0.1:8000";
const number = new Intl.NumberFormat("en-IN");
const compact = new Intl.NumberFormat("en-IN", {
  notation: "compact",
  maximumFractionDigits: 2
});
const money = new Intl.NumberFormat("en-GB", {
  style: "currency",
  currency: "GBP",
  maximumFractionDigits: 2
});

const navItems = [
  { name: "Overview", icon: LayoutDashboard },
  { name: "Dataset Analysis", icon: Database },
  { name: "Pricing Insights", icon: TrendingUp },
  { name: "DML Results", icon: BrainCircuit },
  { name: "Model Evaluation", icon: ChartNoAxesCombined }
];

const colors = ["#6485f5", "#a78bfa", "#f0b65c"];

function Card({ title, subtitle, children, action }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <h3>{title}</h3>
          {subtitle && <p>{subtitle}</p>}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

function Metric({ label, value, icon: Icon, note }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span>{label}</span>
        <div className="stat-icon"><Icon size={19} /></div>
      </div>
      <h2>{value}</h2>
      <div className="stat-change"><span>{note || "Actual dataset value"}</span></div>
    </div>
  );
}

function App() {
  const [active, setActive] = useState("Overview");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [overview, setOverview] = useState(null);
  const [health, setHealth] = useState(null);
  const [monthly, setMonthly] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [noticeOpen, setNoticeOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);
  const [lastUpdated, setLastUpdated] = useState("");

  async function loadDashboard() {
    setLoading(true);
    setError("");
    try {
      const paths = [
        "/api/overview",
        "/api/dataset-health",
        "/api/monthly-trends",
        "/api/price-demand"
      ];
      const results = await Promise.all(paths.map(async (path) => {
        const response = await fetch(`${API}${path}`);
        if (!response.ok) {
          throw new Error(`${path} returned ${response.status}`);
        }
        return response.json();
      }));

      setOverview(results[0]);
      setHealth(results[1]);
      setMonthly(results[2]);
      setProducts(results[3]);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch {
      setError(
        "Unable to connect to the backend. Confirm that FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    Promise.resolve().then(loadDashboard);
  }, []);

  const filteredProducts = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) return products;
    return products.filter((item) =>
      String(item.Description || "").toLowerCase().includes(term)
    );
  }, [products, search]);

  const trends = monthly.map((item) => ({
    ...item,
    month: new Date(`${item.month}-01T00:00:00`).toLocaleDateString(
      "en-GB", { month: "short", year: "2-digit" }
    )
  }));

  const issueData = health ? [
    { name: "Missing customer IDs", value: health.missing_customer_ids },
    { name: "Quantity outliers", value: health.quantity_outlier_count },
    { name: "Price outliers", value: health.price_outlier_count }
  ] : [];

  function navigate(name) {
    setActive(name);
    setSidebarOpen(false);
    setNoticeOpen(false);
    setSettingsOpen(false);
    setHelpOpen(false);
  }

  function renderOverview() {
    if (!overview || !health) return null;
    return (
      <>
        <section className="stats-grid">
          <Metric label="Total Revenue" value={money.format(overview.total_revenue)} icon={DollarSign} />
          <Metric label="Transactions" value={number.format(overview.total_transactions)} icon={ShoppingCart} />
          <Metric label="Average Price" value={money.format(overview.average_price)} icon={Target} />
          <Metric label="Total Quantity" value={compact.format(overview.total_quantity)} icon={Activity} />
        </section>

        <section className="charts-grid">
          <Card title="Revenue & Demand Trends" subtitle="Actual monthly revenue and quantity">
            <div className="chart-legend">
              <span><i className="legend-blue" /> Revenue (£)</span>
              <span><i className="legend-purple" /> Demand (units)</span>
            </div>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#263043" vertical={false} />
                  <XAxis dataKey="month" stroke="#8490a5" tickLine={false} axisLine={false} />
                  <YAxis stroke="#8490a5" tickLine={false} axisLine={false} tickFormatter={compact.format} />
                  <Tooltip />
                  <Area dataKey="revenue" name="Revenue (£)" stroke="#6485f5" fill="#6485f5" fillOpacity={0.18} />
                  <Area dataKey="demand" name="Demand" stroke="#a78bfa" fill="#a78bfa" fillOpacity={0.12} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card title="Dataset Health" subtitle="Missing IDs and detected outliers">
            <div className="donut-wrap">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={issueData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={88} paddingAngle={4}>
                    {issueData.map((item, index) => <Cell key={item.name} fill={colors[index]} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="donut-center">
                <strong>{number.format(health.missing_customer_ids)}</strong>
                <span>Missing IDs</span>
              </div>
            </div>
            <div className="dataset-legend">
              <div><i className="legend-blue" /><span>Missing customer IDs</span><strong>{health.missing_customer_percentage}%</strong></div>
              <div><i className="legend-purple" /><span>Quantity outliers</span><strong>{health.quantity_outlier_percentage}%</strong></div>
              <div><i className="legend-yellow" /><span>Price outliers</span><strong>{health.price_outlier_percentage}%</strong></div>
            </div>
          </Card>
        </section>

        <section className="bottom-grid">
          <Card title="Top Products by Revenue" subtitle="Descriptive product-level data">
            <ProductTable rows={products} />
          </Card>
          <Card title="Dataset Summary" subtitle="Verified backend statistics">
            <InfoRow label="Total records" value={number.format(overview.total_rows)} />
            <InfoRow label="Dataset columns" value={overview.total_columns} />
            <InfoRow label="Missing customer IDs" value={number.format(health.missing_customer_ids)} />
            <InfoRow label="Quantity outliers" value={number.format(health.quantity_outlier_count)} />
            <InfoRow label="Price outliers" value={number.format(health.price_outlier_count)} />
          </Card>
        </section>
      </>
    );
  }

  function renderDataset() {
    if (!overview || !health) return null;
    return (
      <>
        <section className="stats-grid">
          <Metric label="Dataset rows" value={number.format(overview.total_rows)} icon={Database} />
          <Metric label="Columns" value={overview.total_columns} icon={FileBarChart} />
          <Metric label="Missing customer IDs" value={number.format(health.missing_customer_ids)} icon={AlertTriangle} />
          <Metric label="Missing ID rate" value={`${health.missing_customer_percentage}%`} icon={Activity} />
        </section>
        <section className="bottom-grid">
          <Card title="Data quality summary" subtitle="Calculated from the processed dataset">
            <InfoRow label="Missing customer IDs" value={`${number.format(health.missing_customer_ids)} (${health.missing_customer_percentage}%)`} />
            <InfoRow label="Quantity outliers" value={`${number.format(health.quantity_outlier_count)} (${health.quantity_outlier_percentage}%)`} />
            <InfoRow label="Price outliers" value={`${number.format(health.price_outlier_count)} (${health.price_outlier_percentage}%)`} />
            <InfoRow label="Total records" value={number.format(health.total_rows)} />
          </Card>
          <Card title="Data quality distribution" subtitle="Counts by detected issue">
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={issueData} layout="vertical">
                  <XAxis type="number" tickFormatter={compact.format} stroke="#8490a5" />
                  <YAxis type="category" dataKey="name" width={125} stroke="#8490a5" />
                  <Tooltip />
                  <Bar dataKey="value" fill="#829bff" radius={[0, 5, 5, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </section>
        <Card title="Monthly dataset activity" subtitle="Actual monthly revenue and demand">
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#263043" />
                <XAxis dataKey="month" stroke="#8490a5" />
                <YAxis stroke="#8490a5" tickFormatter={compact.format} />
                <Tooltip />
                <Area dataKey="revenue" stroke="#6485f5" fill="#6485f5" fillOpacity={0.2} />
                <Area dataKey="demand" stroke="#a78bfa" fill="#a78bfa" fillOpacity={0.15} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </>
    );
  }

  function renderPricing() {
    return (
      <>
        <div className="notice">
          <Activity size={17} />
          Product metrics below are descriptive statistics, not causal price recommendations.
        </div>
        <Card title="Product price and demand" subtitle="Actual product aggregates from the backend">
          <div className="table-search">
            <Search size={16} />
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search products..." />
            {search && <button onClick={() => setSearch("")} aria-label="Clear search"><X size={15} /></button>}
          </div>
          <ProductTable rows={filteredProducts} />
        </Card>
        <Card title="Price and demand comparison" subtitle="Top products returned by the price-demand endpoint">
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={filteredProducts}>
                <CartesianGrid strokeDasharray="3 3" stroke="#263043" />
                <XAxis dataKey="Description" stroke="#8490a5" tick={{ fontSize: 10 }} />
                <YAxis stroke="#8490a5" tickFormatter={compact.format} />
                <Tooltip />
                <Bar dataKey="price" name="Average price (£)" fill="#6485f5" />
                <Bar dataKey="demand" name="Quantity" fill="#a78bfa" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </>
    );
  }

  function renderDML() {
    return (
      <Card title="Double Machine Learning" subtitle="Causal price-effect estimation">
        <div className="notice">
          <AlertTriangle size={18} />
          DML estimation is not yet implemented in the current repository. No causal estimate is available to display.
        </div>
        <InfoRow label="Candidate treatment" value="Price" />
        <InfoRow label="Candidate outcome" value="Quantity" />
        <InfoRow label="Candidate confounders" value="StockCode, Country, InvoiceDate (under review)" />
        <InfoRow label="Feature readiness validation" value="Implemented" />
        <InfoRow label="Treatment effect" value="Not estimated" />
        <InfoRow label="Confidence interval" value="Not available" />
        <InfoRow label="Causal identification" value="Requires justification" />
        <p className="page-note">The project’s variable-selection report identifies these as candidate variables only. A causal claim requires a defensible identification strategy and an evaluated DML model.</p>
      </Card>
    );
  }

  function renderEvaluation() {
    return (
      <Card title="Model Evaluation" subtitle="Evaluation status">
        <div className="notice">
          <AlertTriangle size={18} />
          No trained DML model or evaluation results were found in the current project files.
        </div>
        <InfoRow label="Model training" value="Not implemented" />
        <InfoRow label="Cross-fitting results" value="Not available" />
        <InfoRow label="RMSE / MAE" value="Not available" />
        <InfoRow label="Treatment effect confidence interval" value="Not available" />
        <InfoRow label="Robustness checks" value="Pending" />
        <p className="page-note">Metrics will appear here after a model is fitted and evaluated on an appropriate validation procedure. No placeholder scores are used.</p>
      </Card>
    );
  }

  function renderContent() {
    if (loading && !overview) return <div className="notice">Loading live backend data...</div>;
    if (error && !overview) return <div className="notice error-notice">{error}<button onClick={loadDashboard}>Retry</button></div>;

    switch (active) {
      case "Overview": return renderOverview();
      case "Dataset Analysis": return renderDataset();
      case "Pricing Insights": return renderPricing();
      case "DML Results": return renderDML();
      case "Model Evaluation": return renderEvaluation();
      default: return renderOverview();
    }
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-icon"><BrainCircuit size={25} /></div>
          <div><h2>Econo<span>Causal</span></h2><p>INTELLIGENT PRICING</p></div>
        </div>
        <div className="workspace">
          <span className="workspace-dot" />
          <div><strong>Team Workspace</strong><small>Group 22 · Infotact</small></div>
          <ChevronDown size={16} />
        </div>
        <p className="nav-heading">WORKSPACE</p>
        <nav className="navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button key={item.name} className={`nav-link ${active === item.name ? "active" : ""}`} onClick={() => navigate(item.name)}>
                <Icon size={19} /><span>{item.name}</span>
              </button>
            );
          })}
        </nav>
        <p className="nav-heading tools-heading">PREFERENCES</p>
        <button className="nav-link" onClick={() => setSettingsOpen(true)}><Settings size={19} /><span>Settings</span></button>
        <button className="nav-link" onClick={() => setHelpOpen(true)}><CircleHelp size={19} /><span>Help & Support</span></button>
        <div className="sidebar-bottom">
          <div className="upgrade-card">
            <div className="upgrade-icon"><BrainCircuit size={18} /></div>
            <strong>Smart Pricing Analytics</strong>
            <p>Explore descriptive analytics and causal ML research.</p>
          </div>
          <div className="profile">
            <div className="avatar">HG</div>
            <div><strong>Hansika Gehlot</strong><small>Team Administrator</small></div>
            <ChevronDown size={16} />
          </div>
        </div>
      </aside>

      {sidebarOpen && <div className="overlay" onClick={() => setSidebarOpen(false)} />}

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button className="mobile-menu" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label="Toggle menu"><Menu /></button>
            <div className="breadcrumb">Workspace <span>/</span> <strong>{active}</strong></div>
          </div>
          <div className="topbar-right">
            <div className="search-box">
              <Search size={17} />
              <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search products..." />
            </div>
            <button className="icon-button" onClick={() => setNoticeOpen(!noticeOpen)} aria-label="Notifications"><Bell size={19} /></button>
            <button className="icon-button" onClick={loadDashboard} disabled={loading} aria-label="Refresh data"><RefreshCw size={18} /></button>
            <div className="top-avatar">HG</div>
          </div>
          {noticeOpen && <div className="notification-popover">No new notifications. Data refresh status: {lastUpdated || "Not refreshed yet"}.</div>}
        </header>

        <div className="page-content">
          <section className="welcome-row">
            <div>
              <div className="eyebrow"><span /> ECONOCAUSAL ANALYTICS WORKSPACE</div>
              <h1>{active}</h1>
              <p>Dynamic Pricing via Double Machine Learning · Team Group 22</p>
            </div>
            <button className="date-button" onClick={loadDashboard}><RefreshCw size={16} /> Refresh data</button>
          </section>

          {error && <div className="notice error-notice">{error}</div>}
          {loading && <div className="notice">Refreshing backend data...</div>}
          {renderContent()}

          <footer className="footer">
            <span>© 2026 EconoCausal · Team Group 22</span>
            <span>Last updated: {lastUpdated || "Not refreshed"}</span>
          </footer>
        </div>
      </main>

      {settingsOpen && (
        <div className="modal-backdrop" onClick={() => setSettingsOpen(false)}>
          <section className="modal-card" onClick={(event) => event.stopPropagation()}>
            <button className="modal-close" onClick={() => setSettingsOpen(false)}><X size={18} /></button>
            <h2>Settings</h2>
            <p>Dashboard preferences</p>
            <InfoRow label="Backend URL" value={API} />
            <InfoRow label="Currency display" value="GBP (£), as recorded in the dataset" />
            <InfoRow label="Data source" value="Processed Online Retail dataset" />
            <button className="date-button" onClick={() => { setSettingsOpen(false); loadDashboard(); }}>Refresh connection</button>
          </section>
        </div>
      )}

      {helpOpen && (
        <div className="modal-backdrop" onClick={() => setHelpOpen(false)}>
          <section className="modal-card" onClick={(event) => event.stopPropagation()}>
            <button className="modal-close" onClick={() => setHelpOpen(false)}><X size={18} /></button>
            <h2>Help & Support</h2>
            <p>EconoCausal dashboard guidance</p>
            <InfoRow label="Overview" value="Dataset-level revenue, transactions and trends" />
            <InfoRow label="Dataset Analysis" value="Missing values and outlier summaries" />
            <InfoRow label="Pricing Insights" value="Descriptive product price and demand data" />
            <InfoRow label="DML Results" value="Causal estimation status and methodology" />
            <InfoRow label="Model Evaluation" value="Model validation status and metrics" />
            <p className="page-note">For this review build, ensure the FastAPI server is running on port 8000.</p>
            <button className="date-button" onClick={() => setHelpOpen(false)}>Close</button>
          </section>
        </div>
      )}
    </div>
  );
}

function InfoRow({ label, value }) {
  return <div className="info-row"><span>{label}</span><strong>{value}</strong></div>;
}

function ProductTable({ rows }) {
  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead><tr><th>Product</th><th>Average price</th><th>Demand</th><th>Revenue</th></tr></thead>
        <tbody>
          {rows.map((item, index) => (
            <tr key={`${item.Description}-${index}`}>
              <td>{item.Description}</td>
              <td>{money.format(item.price)}</td>
              <td>{number.format(item.demand)}</td>
              <td>{money.format(item.revenue)}</td>
            </tr>
          ))}
          {rows.length === 0 && <tr><td colSpan="4">No matching products found.</td></tr>}
        </tbody>
      </table>
    </div>
  );
}

export default App;

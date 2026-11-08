import { useEffect, useState } from "react";
import {
  LayoutDashboard, Database, TrendingUp, BrainCircuit,
  ChartNoAxesCombined, Settings, Bell, Search, Menu,
  ArrowUpRight, DollarSign, ShoppingCart, Activity,
  CalendarDays, ChevronDown, CircleHelp, Target, Zap
} from "lucide-react";

import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, BarChart, Bar, PieChart, Pie, Cell
} from "recharts";

import "./App.css";

const API = "http://127.0.0.1:8000";

const numberFormat = new Intl.NumberFormat("en-IN");
const compactFormat = new Intl.NumberFormat("en-IN", {
  notation: "compact",
  maximumFractionDigits: 2
});

const currencyFormat = new Intl.NumberFormat("en-GB", {
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

const chartColors = ["#6485f5", "#a78bfa", "#f0b65c"];

function App() {
  const [active, setActive] = useState("Overview");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [overview, setOverview] = useState(null);
  const [health, setHealth] = useState(null);
  const [monthlyData, setMonthlyData] = useState([]);
  const [pricingData, setPricingData] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        const endpoints = [
          "/api/overview",
          "/api/dataset-health",
          "/api/monthly-trends",
          "/api/price-demand"
        ];

        const responses = await Promise.all(
          endpoints.map(async (endpoint) => {
            const response = await fetch(`${API}${endpoint}`);

            if (!response.ok) {
              throw new Error(`API request failed: ${endpoint}`);
            }

            return response.json();
          })
        );

        if (!cancelled) {
          setOverview(responses[0]);
          setHealth(responses[1]);
          setMonthlyData(responses[2]);
          setPricingData(responses[3]);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            "Unable to load dashboard data. Please check whether the Python backend is running on port 8000."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  const stats = overview
    ? [
        {
          label: "Total Revenue",
          value: currencyFormat.format(overview.total_revenue),
          icon: DollarSign
        },
        {
          label: "Total Transactions",
          value: numberFormat.format(overview.total_transactions),
          icon: ShoppingCart
        },
        {
          label: "Average Price",
          value: currencyFormat.format(overview.average_price),
          icon: Target
        },
        {
          label: "Total Quantity",
          value: compactFormat.format(overview.total_quantity),
          icon: Activity
        }
      ]
    : [];

  const trends = monthlyData.map((item) => ({
    ...item,
    month: new Date(`${item.month}-01T00:00:00`).toLocaleDateString(
      "en-GB",
      { month: "short", year: "2-digit" }
    )
  }));

  const issueData = health
    ? [
        {
          name: "Missing Customer IDs",
          value: health.missing_customer_ids
        },
        {
          name: "Quantity Outliers",
          value: health.quantity_outlier_count
        },
        {
          name: "Price Outliers",
          value: health.price_outlier_count
        }
      ]
    : [];

  const products = pricingData.map((item) => ({
    ...item,
    product:
      item.Description.length > 19
        ? `${item.Description.slice(0, 17)}...`
        : item.Description
  }));

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-icon">
            <BrainCircuit size={25} />
          </div>
          <div>
            <h2>Econo<span>Causal</span></h2>
            <p>INTELLIGENT PRICING</p>
          </div>
        </div>

        <div className="workspace">
          <span className="workspace-dot"></span>
          <div>
            <strong>Team Workspace</strong>
            <small>Group 22 · Infotact</small>
          </div>
          <ChevronDown size={16} />
        </div>

        <p className="nav-heading">WORKSPACE</p>

        <nav className="navigation">
          {navItems.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.name}
                className={`nav-link ${active === item.name ? "active" : ""}`}
                onClick={() => {
                  setActive(item.name);
                  setSidebarOpen(false);
                }}
              >
                <Icon size={19} />
                <span>{item.name}</span>
                {item.name === "DML Results" && (
                  <span className="soon-dot"></span>
                )}
              </button>
            );
          })}
        </nav>

        <p className="nav-heading tools-heading">PREFERENCES</p>

        <button className="nav-link">
          <Settings size={19} />
          <span>Settings</span>
        </button>

        <button className="nav-link">
          <CircleHelp size={19} />
          <span>Help & Support</span>
        </button>

        <div className="sidebar-bottom">
          <div className="upgrade-card">
            <div className="upgrade-icon">
              <Zap size={18} />
            </div>
            <strong>Smart Pricing Analytics</strong>
            <p>Explore data-driven pricing insights with causal ML.</p>
          </div>

          <div className="profile">
            <div className="avatar">HG</div>
            <div>
              <strong>Hansika Gehlot</strong>
              <small>Team Administrator</small>
            </div>
            <ChevronDown size={16} />
          </div>
        </div>
      </aside>

      {sidebarOpen && (
        <div
          className="overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="mobile-menu"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              <Menu />
            </button>

            <div className="breadcrumb">
              Workspace <span>/</span> <strong>{active}</strong>
            </div>
          </div>

          <div className="topbar-right">
            <div className="search-box">
              <Search size={17} />
              <input placeholder="Search analytics..." />
            </div>

            <button className="icon-button notification">
              <Bell size={19} />
              <i></i>
            </button>

            <div className="top-avatar">HG</div>
          </div>
        </header>

        <div className="page-content">
          <section className="welcome-row">
            <div>
              <div className="eyebrow">
                <span></span> ANALYTICS WORKSPACE
              </div>

              <h1>
                {active === "Overview" ? "Dashboard Overview" : active}
              </h1>

              <p>
                Monitor pricing performance and explore business insights.
              </p>
            </div>

            <button className="date-button">
              <CalendarDays size={17} />
              Full Dataset
              <ChevronDown size={15} />
            </button>
          </section>

          <div className="notice">
            <Activity size={17} />
            <span>
              <strong>Live dataset:</strong> Dashboard statistics are fetched
              from the EconoCausal FastAPI backend.
            </span>
          </div>

          {loading && (
            <div className="notice">
              Loading actual dataset statistics...
            </div>
          )}

          {error && (
            <div
              className="notice"
              style={{ borderColor: "#a94c5b", color: "#ffb5bd" }}
            >
              {error}
            </div>
          )}

          {!loading && !error && overview && health && (
            <>
              <section className="stats-grid">
                {stats.map((stat) => {
                  const Icon = stat.icon;

                  return (
                    <div className="stat-card" key={stat.label}>
                      <div className="stat-top">
                        <span>{stat.label}</span>
                        <div className="stat-icon">
                          <Icon size={19} />
                        </div>
                      </div>

                      <h2>{stat.value}</h2>

                      <div className="stat-change up">
                        <ArrowUpRight size={16} />
                        <span>Actual dataset value</span>
                      </div>
                    </div>
                  );
                })}
              </section>

              <section className="charts-grid">
                <div className="panel revenue-panel">
                  <div className="panel-heading">
                    <div>
                      <h3>Revenue & Demand Trends</h3>
                      <p>Actual monthly revenue and quantity demand</p>
                    </div>
                    <button className="more-button">Monthly</button>
                  </div>

                  <div className="chart-legend">
                    <span>
                      <i className="legend-blue"></i> Revenue (£)
                    </span>
                    <span>
                      <i className="legend-purple"></i> Demand (Units)
                    </span>
                  </div>

                  <div className="chart-container">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={trends}>
                        <defs>
                          <linearGradient
                            id="revenueGradient"
                            x1="0"
                            y1="0"
                            x2="0"
                            y2="1"
                          >
                            <stop
                              offset="0%"
                              stopColor="#6485f5"
                              stopOpacity={0.25}
                            />
                            <stop
                              offset="95%"
                              stopColor="#6485f5"
                              stopOpacity={0}
                            />
                          </linearGradient>

                          <linearGradient
                            id="demandGradient"
                            x1="0"
                            y1="0"
                            x2="0"
                            y2="1"
                          >
                            <stop
                              offset="0%"
                              stopColor="#a78bfa"
                              stopOpacity={0.18}
                            />
                            <stop
                              offset="95%"
                              stopColor="#a78bfa"
                              stopOpacity={0}
                            />
                          </linearGradient>
                        </defs>

                        <CartesianGrid
                          strokeDasharray="3 3"
                          stroke="#263043"
                          vertical={false}
                        />

                        <XAxis
                          dataKey="month"
                          stroke="#8490a5"
                          tickLine={false}
                          axisLine={false}
                          minTickGap={18}
                        />

                        <YAxis
                          stroke="#8490a5"
                          tickLine={false}
                          axisLine={false}
                          tickFormatter={compactFormat.format}
                        />

                        <Tooltip
                          formatter={(value, name) => [
                            numberFormat.format(value),
                            name === "revenue" ? "Revenue (£)" : "Demand (units)"
                          ]}
                          contentStyle={{
                            background: "#151e2d",
                            border: "1px solid #303b50",
                            borderRadius: 10
                          }}
                        />

                        <Area
                          type="monotone"
                          dataKey="revenue"
                          stroke="#6485f5"
                          strokeWidth={2.5}
                          fill="url(#revenueGradient)"
                        />

                        <Area
                          type="monotone"
                          dataKey="demand"
                          stroke="#a78bfa"
                          strokeWidth={2.5}
                          fill="url(#demandGradient)"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="panel dataset-panel">
                  <div className="panel-heading">
                    <div>
                      <h3>Dataset Health</h3>
                      <p>Missing IDs and detected outlier counts</p>
                    </div>
                    <button className="dots-button">•••</button>
                  </div>

                  <div className="donut-wrap">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={issueData}
                          dataKey="value"
                          nameKey="name"
                          innerRadius={66}
                          outerRadius={91}
                          paddingAngle={4}
                          stroke="none"
                        >
                          {issueData.map((entry, index) => (
                            <Cell
                              key={entry.name}
                              fill={chartColors[index]}
                            />
                          ))}
                        </Pie>

                        <Tooltip
                          formatter={(value) => numberFormat.format(value)}
                          contentStyle={{
                            background: "#151e2d",
                            border: "1px solid #303b50",
                            borderRadius: 10
                          }}
                        />
                      </PieChart>
                    </ResponsiveContainer>

                    <div className="donut-center">
                      <strong>
                        {numberFormat.format(
                          health.missing_customer_ids
                        )}
                      </strong>
                      <span>Missing IDs</span>
                    </div>
                  </div>

                  <div className="dataset-legend">
                    <div>
                      <i className="legend-blue"></i>
                      <span>Missing Customer IDs</span>
                      <strong>
                        {health.missing_customer_percentage}%
                      </strong>
                    </div>

                    <div>
                      <i className="legend-purple"></i>
                      <span>Quantity Outliers</span>
                      <strong>
                        {health.quantity_outlier_percentage}%
                      </strong>
                    </div>

                    <div>
                      <i className="legend-yellow"></i>
                      <span>Price Outliers</span>
                      <strong>
                        {health.price_outlier_percentage}%
                      </strong>
                    </div>
                  </div>
                </div>
              </section>

              <section className="bottom-grid">
                <div className="panel pricing-panel">
                  <div className="panel-heading">
                    <div>
                      <h3>Price vs Demand Analysis</h3>
                      <p>Actual top five products by revenue</p>
                    </div>
                    <button className="more-button">
                      Live Data <ArrowUpRight size={15} />
                    </button>
                  </div>

                  <div className="chart-container bar-chart">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={products} barGap={9}>
                        <CartesianGrid
                          strokeDasharray="3 3"
                          stroke="#263043"
                          vertical={false}
                        />

                        <XAxis
                          dataKey="product"
                          stroke="#8490a5"
                          tickLine={false}
                          axisLine={false}
                          interval={0}
                          tick={{ fontSize: 9 }}
                        />

                        <YAxis
                          stroke="#8490a5"
                          tickLine={false}
                          axisLine={false}
                          tickFormatter={compactFormat.format}
                        />

                        <Tooltip
                          formatter={(value, name) => [
                            numberFormat.format(value),
                            name
                          ]}
                          contentStyle={{
                            background: "#151e2d",
                            border: "1px solid #303b50",
                            borderRadius: 10
                          }}
                        />

                        <Bar
                          dataKey="price"
                          name="Average Price (£)"
                          fill="#6485f5"
                          radius={[5, 5, 0, 0]}
                        />

                        <Bar
                          dataKey="demand"
                          name="Demand (Units)"
                          fill="#a78bfa"
                          radius={[5, 5, 0, 0]}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="panel status-panel">
                  <div className="panel-heading">
                    <div>
                      <h3>Dataset Summary</h3>
                      <p>Verified backend statistics</p>
                    </div>
                  </div>

                  <div className="progress-item">
                    <div>
                      <span>Total Records</span>
                      <strong>{numberFormat.format(overview.total_rows)}</strong>
                    </div>
                    <div className="progress-track">
                      <span style={{ width: "100%" }}></span>
                    </div>
                  </div>

                  <div className="progress-item">
                    <div>
                      <span>Dataset Columns</span>
                      <strong>{overview.total_columns}</strong>
                    </div>
                    <div className="progress-track">
                      <span style={{ width: "100%" }}></span>
                    </div>
                  </div>

                  <div className="progress-item">
                    <div>
                      <span>Quantity Outliers</span>
                      <strong>{numberFormat.format(health.quantity_outlier_count)}</strong>
                    </div>
                    <div className="progress-track">
                      <span
                        style={{
                          width: `${Math.max(health.quantity_outlier_percentage, 1)}%`
                        }}
                      ></span>
                    </div>
                  </div>

                  <div className="progress-item">
                    <div>
                      <span>Price Outliers</span>
                      <strong>{numberFormat.format(health.price_outlier_count)}</strong>
                    </div>
                    <div className="progress-track">
                      <span
                        style={{
                          width: `${Math.max(health.price_outlier_percentage, 1)}%`
                        }}
                      ></span>
                    </div>
                  </div>

                  <div className="project-footer">
                    <span className="status-dot"></span>
                    Team Group 22 <span>·</span> Infotact Solutions
                  </div>
                </div>
              </section>
            </>
          )}

          <footer className="footer">
            <span>© 2026 EconoCausal · Team Group 22</span>
            <span>Dynamic Pricing via Double Machine Learning</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default App;

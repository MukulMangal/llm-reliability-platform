import {
  Activity,
  ArrowUpRight,
  Bot,
  CreditCard,
  LayoutDashboard,
  Link2,
  Menu,
  RefreshCcw,
  Search,
  Settings,
  ShieldCheck,
  WalletCards,
  X,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import AgentPage from "./components/AgentPage";
import PaymentsPage from "./components/PaymentsPage";
import PaymentLinksPage from "./components/PaymentLinksPage";
import RefundsPage from "./components/RefundsPage";
import ActivityPage from "./components/ActivityPage";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const navigation = [
  {
    label: "Workspace",
    items: [
      { label: "Overview", icon: LayoutDashboard },
      { label: "Payments", icon: CreditCard },
      { label: "Payment Links", icon: Link2 },
      { label: "Refunds", icon: RefreshCcw },
    ],
  },
  {
    label: "Automation",
    items: [
      { label: "AI Agent", icon: Bot },
      { label: "Activity", icon: Activity },
    ],
  },
];

const formatCurrency = (amount, currency = "INR") => {
  if (typeof amount !== "number") return "₹0";

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(amount / 100);
};

const formatPaymentStatus = (status) => {
  if (!status) return "Unknown";

  return status.charAt(0).toUpperCase() + status.slice(1);
};

const getCustomerLabel = (payment) => {
  return (
    payment?.email ||
    payment?.contact ||
    payment?.method ||
    "Customer"
  );
};

const formatRelativeTime = (timestamp) => {
  if (!timestamp) return "—";

  const createdAt =
    typeof timestamp === "number"
      ? new Date(timestamp * 1000)
      : new Date(timestamp);

  if (Number.isNaN(createdAt.getTime())) return "—";

  const diffMs = Date.now() - createdAt.getTime();
  const diffMinutes = Math.floor(diffMs / 60000);

  if (diffMinutes < 1) return "Just now";
  if (diffMinutes < 60) return `${diffMinutes} min ago`;

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours} hr ago`;

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays} day${diffDays === 1 ? "" : "s"} ago`;

  return createdAt.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
  });
};

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activePage, setActivePage] = useState("Overview");

  const handleNavigation = (label) => {
    setActivePage(label);
    setSidebarOpen(false);
  };

  const renderPage = () => {
    switch (activePage) {
      case "AI Agent":
        return <AgentPage />;

      case "Payments":
        return <PaymentsPage />;

      case "Payment Links":
        return <PaymentLinksPage />;

      case "Refunds":
        return <RefundsPage />;

      case "Activity":
        return <ActivityPage />;

      case "Overview":
      default:
        return (
          <OverviewPage
            onOpenAgent={() => setActivePage("AI Agent")}
            onOpenPayments={() => setActivePage("Payments")}
            onOpenRefunds={() => setActivePage("Refunds")}
            onOpenActivity={() => setActivePage("Activity")}
          />
        );
    }
  };

  return (
    <div className="app-shell">
      {sidebarOpen && (
        <button
          className="mobile-overlay"
          type="button"
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark">
            <span />
            <span />
            <span />
          </div>

          <div>
            <div className="brand-name">PayPilot</div>
            <div className="brand-caption">Payment intelligence</div>
          </div>

          <button
            className="sidebar-close"
            type="button"
            aria-label="Close navigation"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={18} />
          </button>
        </div>

        <nav className="navigation">
          {navigation.map((section) => (
            <div className="nav-section" key={section.label}>
              <div className="nav-section-label">{section.label}</div>

              <div className="nav-items">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activePage === item.label;

                  return (
                    <button
                      className={`nav-item ${
                        isActive ? "nav-item-active" : ""
                      }`}
                      key={item.label}
                      type="button"
                      onClick={() => handleNavigation(item.label)}
                    >
                      <Icon size={18} strokeWidth={1.8} />
                      <span>{item.label}</span>

                      {item.label === "AI Agent" && (
                        <span className="nav-ai-badge">AI</span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <button
            className={`nav-item ${
              activePage === "Settings" ? "nav-item-active" : ""
            }`}
            type="button"
            onClick={() => handleNavigation("Settings")}
          >
            <Settings size={18} strokeWidth={1.8} />
            <span>Settings</span>
          </button>

          <div className="environment-card">
            <div className="environment-icon">
              <ShieldCheck size={16} />
            </div>

            <div className="environment-copy">
              <span>Environment</span>
              <strong>Razorpay Test Mode</strong>
            </div>

            <span className="status-dot" />
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="menu-button"
              type="button"
              aria-label="Open navigation"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu size={20} />
            </button>

            <div className="breadcrumb">
              <span>Workspace</span>
              <span className="breadcrumb-separator">/</span>
              <strong>{activePage}</strong>
            </div>
          </div>

          <div className="topbar-actions">
            <button className="search-button" type="button">
              <Search size={17} />
              <span>Search</span>
              <kbd>⌘ K</kbd>
            </button>

            <div className="mode-pill">
              <span className="status-dot" />
              Test Mode
            </div>

            <div className="profile">
              <div className="profile-avatar">MK</div>

              <div className="profile-copy">
                <strong>Mukul</strong>
                <span>Merchant</span>
              </div>
            </div>
          </div>
        </header>

        <div className="page-content">{renderPage()}</div>
      </main>
    </div>
  );
}

function OverviewPage({
  onOpenAgent,
  onOpenPayments,
  onOpenRefunds,
  onOpenActivity,
}) {
  const [payments, setPayments] = useState([]);
  const [refunds, setRefunds] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchOverviewData = async () => {
    setLoading(true);
    setError("");

    try {
      const [paymentsResponse, refundsResponse, activityResponse] =
        await Promise.all([
          fetch(`${API_URL}/payments/?count=100`),
          fetch(`${API_URL}/refunds/?count=100`),
          fetch(`${API_URL}/activity/?limit=100`),
        ]);

      if (!paymentsResponse.ok) {
        throw new Error("Unable to load payment data.");
      }

      if (!refundsResponse.ok) {
        throw new Error("Unable to load refund data.");
      }

      if (!activityResponse.ok) {
        throw new Error("Unable to load activity data.");
      }

      const [paymentsData, refundsData, activityData] =
        await Promise.all([
          paymentsResponse.json(),
          refundsResponse.json(),
          activityResponse.json(),
        ]);

      setPayments(paymentsData?.payments || []);
      setRefunds(refundsData?.refunds || []);
      setActivities(activityData?.activities || []);
    } catch (err) {
      setError(err.message || "Unable to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverviewData();
  }, []);

  const overview = useMemo(() => {
    const totalPayments = payments.length;

    const capturedPayments = payments.filter(
      (payment) => payment?.status === "captured"
    );

    const paymentVolume = payments.reduce(
      (total, payment) =>
        total + (typeof payment?.amount === "number" ? payment.amount : 0),
      0
    );

    const capturedVolume = capturedPayments.reduce(
      (total, payment) =>
        total + (typeof payment?.amount === "number" ? payment.amount : 0),
      0
    );

    const refundVolume = refunds.reduce(
      (total, refund) =>
        total + (typeof refund?.amount === "number" ? refund.amount : 0),
      0
    );

    const successRate =
      totalPayments > 0
        ? (capturedPayments.length / totalPayments) * 100
        : 0;

    const successfulActivities = activities.filter(
      (activity) => activity?.success === true
    );

    const blockedActivities = activities.filter(
      (activity) =>
        activity?.status === "validation_failed" ||
        activity?.success === false
    );

    const reliabilityScores = activities
      .map((activity) => activity?.reliability_score)
      .filter((score) => typeof score === "number");

    const reliability =
      reliabilityScores.length > 0
        ? reliabilityScores.reduce((sum, score) => sum + score, 0) /
          reliabilityScores.length
        : null;

    return {
      totalPayments,
      capturedPayments: capturedPayments.length,
      paymentVolume,
      capturedVolume,
      refundVolume,
      successRate,
      successfulActivities: successfulActivities.length,
      blockedActivities: blockedActivities.length,
      reliability,
    };
  }, [payments, refunds, activities]);

  const recentPayments = useMemo(() => {
    return [...payments]
      .sort((a, b) => {
        const timeA =
          typeof a?.created_at === "number"
            ? a.created_at
            : new Date(a?.created_at || 0).getTime();

        const timeB =
          typeof b?.created_at === "number"
            ? b.created_at
            : new Date(b?.created_at || 0).getTime();

        return timeB - timeA;
      })
      .slice(0, 5);
  }, [payments]);

  const statusBreakdown = useMemo(() => {
    return {
      captured: payments.filter((payment) => payment?.status === "captured")
        .length,
      pending: payments.filter((payment) => payment?.status === "pending")
        .length,
      failed: payments.filter((payment) => payment?.status === "failed")
        .length,
    };
  }, [payments]);

  return (
    <>
      <section className="page-heading">
        <div>
          <div className="eyebrow">
            <span className="eyebrow-line" />
            PAYMENT OPERATIONS
          </div>

          <h1>Good afternoon, Mukul.</h1>

          <p>
            Monitor your payments and let AI handle the routine operations.
          </p>
        </div>

        <button
          className="agent-button"
          type="button"
          onClick={onOpenAgent}
        >
          <Bot size={17} />
          Open AI Agent
        </button>
      </section>

      {error && (
        <section
          className="panel"
          style={{
            marginBottom: "18px",
            padding: "16px 18px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "16px",
          }}
        >
          <div>
            <div className="panel-title">Dashboard data unavailable</div>
            <div className="panel-subtitle">{error}</div>
          </div>

          <button
            className="text-button"
            type="button"
            onClick={fetchOverviewData}
          >
            <RefreshCcw size={14} />
            Retry
          </button>
        </section>
      )}

      <section className="metrics-grid">
        <article className="metric-card">
          <div className="metric-header">
            <div className="metric-icon">
              <WalletCards size={17} strokeWidth={1.8} />
            </div>

            <span className="metric-change">Live</span>
          </div>

          <div className="metric-value">
            {loading
              ? "—"
              : formatCurrency(
                  overview.capturedVolume || overview.paymentVolume
                )}
          </div>

          <div className="metric-label">Payment volume</div>
        </article>

        <article className="metric-card">
          <div className="metric-header">
            <div className="metric-icon">
              <CreditCard size={17} strokeWidth={1.8} />
            </div>

            <span className="metric-change">Live</span>
          </div>

          <div className="metric-value">
            {loading ? "—" : overview.capturedPayments}
          </div>

          <div className="metric-label">Captured payments</div>
        </article>

        <article className="metric-card">
          <div className="metric-header">
            <div className="metric-icon">
              <ShieldCheck size={17} strokeWidth={1.8} />
            </div>

            <span className="metric-change">Live</span>
          </div>

          <div className="metric-value">
            {loading
              ? "—"
              : `${overview.successRate.toFixed(1)}%`}
          </div>

          <div className="metric-label">Payment success rate</div>
        </article>

        <article className="metric-card">
          <div className="metric-header">
            <div className="metric-icon">
              <RefreshCcw size={17} strokeWidth={1.8} />
            </div>

            <span className="metric-change">Live</span>
          </div>

          <div className="metric-value">
            {loading ? "—" : formatCurrency(overview.refundVolume)}
          </div>

          <div className="metric-label">Refund volume</div>
        </article>
      </section>

      <section className="dashboard-grid">
        <article className="panel transactions-panel">
          <div className="panel-header">
            <div>
              <div className="panel-title">Recent payments</div>
              <div className="panel-subtitle">
                Latest activity from Razorpay Test Mode
              </div>
            </div>

            <button
              className="text-button"
              type="button"
              onClick={onOpenPayments}
            >
              View all
              <ArrowUpRight size={14} />
            </button>
          </div>

          <div className="transaction-table">
            <div className="table-header">
              <span>Payment</span>
              <span>Customer</span>
              <span>Amount</span>
              <span>Status</span>
              <span>Time</span>
            </div>

            {loading ? (
              <div className="operations-state">
                <div className="operations-spinner" />
                <span>Loading payments...</span>
              </div>
            ) : recentPayments.length === 0 ? (
              <div className="operations-state">
                <CreditCard size={18} />
                <strong>No payments yet</strong>
                <span>
                  Completed Razorpay Test Mode payments will appear here.
                </span>
              </div>
            ) : (
              recentPayments.map((payment) => {
                const status = formatPaymentStatus(payment?.status);

                return (
                  <div
                    className="transaction-row"
                    key={payment?.id}
                  >
                    <div className="payment-id">
                      <div className="payment-icon">
                        <CreditCard size={15} />
                      </div>

                      <span>{payment?.id || "—"}</span>
                    </div>

                    <span className="customer-name">
                      {getCustomerLabel(payment)}
                    </span>

                    <strong className="transaction-amount">
                      {formatCurrency(
                        payment?.amount,
                        payment?.currency || "INR"
                      )}
                    </strong>

                    <span
                      className={`status-badge status-${(
                        payment?.status || "unknown"
                      ).toLowerCase()}`}
                    >
                      <span />
                      {status}
                    </span>

                    <span className="transaction-time">
                      {formatRelativeTime(payment?.created_at)}
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </article>

        <article className="panel agent-panel">
          <div className="agent-panel-glow" />

          <div className="agent-panel-content">
            <div className="agent-icon-large">
              <Bot size={21} />
            </div>

            <div className="agent-panel-label">AI OPERATIONS AGENT</div>

            <h2>
              Your payments,
              <br />
              <span>on command.</span>
            </h2>

            <p>
              Create payment links, inspect transactions, and manage
              refunds using natural language.
            </p>

            <div className="agent-suggestion">
              <span>Try</span>
              <strong>
                “Create a ₹2,500 payment link for an invoice”
              </strong>
            </div>

            <button
              className="agent-launch-button"
              type="button"
              onClick={onOpenAgent}
            >
              <Bot size={17} />
              Start a conversation
              <ArrowUpRight size={16} />
            </button>
          </div>
        </article>
      </section>

      <section className="bottom-grid">
        <article className="panel activity-panel">
          <div className="panel-header">
            <div>
              <div className="panel-title">Payment status</div>
              <div className="panel-subtitle">
                Current Razorpay Test Mode distribution
              </div>
            </div>

            <button
              className="text-button"
              type="button"
              onClick={onOpenPayments}
            >
              Payments
              <ArrowUpRight size={14} />
            </button>
          </div>

          <div
            style={{
              display: "grid",
              gap: "18px",
              padding: "20px 0 4px",
            }}
          >
            {[
              {
                label: "Captured",
                value: statusBreakdown.captured,
              },
              {
                label: "Pending",
                value: statusBreakdown.pending,
              },
              {
                label: "Failed",
                value: statusBreakdown.failed,
              },
            ].map((item) => {
              const percentage =
                payments.length > 0
                  ? (item.value / payments.length) * 100
                  : 0;

              return (
                <div key={item.label}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: "8px",
                      fontSize: "12px",
                    }}
                  >
                    <span style={{ color: "var(--text-secondary)" }}>
                      {item.label}
                    </span>

                    <strong>{item.value}</strong>
                  </div>

                  <div
                    style={{
                      height: "6px",
                      borderRadius: "999px",
                      background: "rgba(255,255,255,0.06)",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        width: `${percentage}%`,
                        height: "100%",
                        borderRadius: "999px",
                        background: "var(--accent)",
                        transition: "width 300ms ease",
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="reliability-note">
            <CreditCard size={15} />
            {loading
              ? "Loading live payment data..."
              : `${overview.totalPayments} payment${
                  overview.totalPayments === 1 ? "" : "s"
                } retrieved from Razorpay.`}
          </div>
        </article>

        <article className="panel reliability-panel">
          <div className="panel-header">
            <div>
              <div className="panel-title">Agent reliability</div>
              <div className="panel-subtitle">
                Based on recorded PayPilot operations
              </div>
            </div>

            <ShieldCheck size={18} className="panel-header-icon" />
          </div>

          <div className="reliability-score">
            <div className="score-ring">
              <div className="score-inner">
                <strong>
                  {loading || overview.reliability === null
                    ? "—"
                    : `${Math.round(overview.reliability * 100)}%`}
                </strong>

                <span>
                  {overview.reliability === null
                    ? "No data"
                    : "Verified"}
                </span>
              </div>
            </div>

            <div className="reliability-stats">
              <div>
                <strong>{activities.length}</strong>
                <span>Operations</span>
              </div>

              <div>
                <strong>{overview.successfulActivities}</strong>
                <span>Completed</span>
              </div>

              <div>
                <strong>{overview.blockedActivities}</strong>
                <span>Blocked</span>
              </div>
            </div>
          </div>

          <div className="reliability-note">
            <ShieldCheck size={15} />
            Financial actions are verified before execution.
          </div>

          {activities.length > 0 && (
            <button
              className="text-button"
              type="button"
              onClick={onOpenActivity}
              style={{ marginTop: "14px" }}
            >
              View activity
              <ArrowUpRight size={14} />
            </button>
          )}
        </article>
      </section>
    </>
  );
}

export default App;
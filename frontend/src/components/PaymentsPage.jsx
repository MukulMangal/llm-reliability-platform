import {
  ArrowUpRight,
  CreditCard,
  RefreshCcw,
  Search,
  ShieldCheck,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function formatAmount(amount, currency = "INR") {
  if (typeof amount !== "number") {
    return "—";
  }

  if (currency === "INR") {
    return `₹${(amount / 100).toLocaleString("en-IN")}`;
  }

  return `${currency} ${(amount / 100).toLocaleString()}`;
}

function formatDate(timestamp) {
  if (!timestamp) {
    return "—";
  }

  return new Date(timestamp * 1000).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getStatusClass(status) {
  return `payment-status payment-status-${String(
    status || "unknown",
  ).toLowerCase()}`;
}

export default function PaymentsPage() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  const loadPayments = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/payments/?count=100`);

      if (!response.ok) {
        throw new Error("Unable to load payments.");
      }

      const data = await response.json();

      setPayments(Array.isArray(data.payments) ? data.payments : []);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load payments.",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPayments();
  }, []);

  const filteredPayments = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return payments;
    }

    return payments.filter((payment) =>
      [
        payment.id,
        payment.status,
        payment.method,
        payment.email,
        payment.contact,
      ]
        .filter(Boolean)
        .some((value) =>
          String(value).toLowerCase().includes(query),
        ),
    );
  }, [payments, search]);

  const capturedAmount = payments
    .filter((payment) => payment.status === "captured")
    .reduce((total, payment) => total + (payment.amount || 0), 0);

  return (
    <div className="operations-page">
      <section className="operations-heading">
        <div>
          <div className="eyebrow">
            <span className="eyebrow-line" />
            PAYMENT OPERATIONS
          </div>

          <h1>Payments</h1>

          <p>
            Monitor transactions processed through your Razorpay
            account.
          </p>
        </div>

        <button
          className="operations-refresh-button"
          type="button"
          onClick={loadPayments}
          disabled={loading}
        >
          <RefreshCcw size={15} />
          Refresh
        </button>
      </section>

      <section className="operations-stats">
        <article className="operation-stat-card">
          <div className="operation-stat-icon">
            <CreditCard size={17} />
          </div>
          <span>Total payments</span>
          <strong>{payments.length}</strong>
        </article>

        <article className="operation-stat-card">
          <div className="operation-stat-icon">
            <ShieldCheck size={17} />
          </div>
          <span>Captured payments</span>
          <strong>
            {
              payments.filter(
                (payment) => payment.status === "captured",
              ).length
            }
          </strong>
        </article>

        <article className="operation-stat-card">
          <div className="operation-stat-icon">
            <CreditCard size={17} />
          </div>
          <span>Captured volume</span>
          <strong>
            {formatAmount(capturedAmount)}
          </strong>
        </article>
      </section>

      <article className="panel operations-table-panel">
        <div className="panel-header">
          <div>
            <div className="panel-title">All payments</div>
            <div className="panel-subtitle">
              Live data from Razorpay Test Mode
            </div>
          </div>

          <div className="operations-search">
            <Search size={14} />
            <input
              type="search"
              placeholder="Search payments"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>
        </div>

        {loading ? (
          <div className="operations-state">
            <div className="operations-spinner" />
            <strong>Loading payments</strong>
            <span>Fetching the latest Razorpay transactions.</span>
          </div>
        ) : error ? (
          <div className="operations-state operations-state-error">
            <div className="operations-state-icon">
              <RefreshCcw size={18} />
            </div>
            <strong>Unable to load payments</strong>
            <span>{error}</span>
            <button
              className="operations-state-button"
              type="button"
              onClick={loadPayments}
            >
              Try again
            </button>
          </div>
        ) : filteredPayments.length === 0 ? (
          <div className="operations-state">
            <div className="operations-state-icon">
              <CreditCard size={20} />
            </div>

            <strong>
              {payments.length === 0
                ? "No payments yet"
                : "No matching payments"}
            </strong>

            <span>
              {payments.length === 0
                ? "Payments will appear here once a customer completes a transaction."
                : "Try a different payment ID or status."}
            </span>
          </div>
        ) : (
          <div className="operations-table-wrapper">
            <div className="operations-table-header">
              <span>Payment</span>
              <span>Amount</span>
              <span>Status</span>
              <span>Method</span>
              <span>Created</span>
              <span />
            </div>

            {filteredPayments.map((payment) => (
              <div
                className="operations-table-row"
                key={payment.id}
              >
                <div className="operation-primary">
                  <div className="operation-row-icon">
                    <CreditCard size={14} />
                  </div>

                  <div>
                    <strong>{payment.id}</strong>
                    <span>
                      {payment.email ||
                        payment.contact ||
                        "Razorpay payment"}
                    </span>
                  </div>
                </div>

                <strong className="operation-amount">
                  {formatAmount(
                    payment.amount,
                    payment.currency,
                  )}
                </strong>

                <span className={getStatusClass(payment.status)}>
                  <span />
                  {payment.status || "Unknown"}
                </span>

                <span className="operation-secondary">
                  {payment.method || "—"}
                </span>

                <span className="operation-secondary">
                  {formatDate(payment.created_at)}
                </span>

                <button
                  className="operation-icon-button"
                  type="button"
                  aria-label={`View ${payment.id}`}
                >
                  <ArrowUpRight size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </article>
    </div>
  );
}
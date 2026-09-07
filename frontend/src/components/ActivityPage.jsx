import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  Bot,
  CheckCircle2,
  Clock3,
  RefreshCcw,
  ShieldCheck,
  XCircle,
} from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const formatDate = (timestamp) => {
  if (!timestamp) return "—";

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(timestamp));
};

const formatOperation = (operation) => {
  if (!operation) return "Unknown operation";

  return operation
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

const getStatusClass = (status) => {
  switch (status) {
    case "completed":
      return "activity-status activity-status-success";

    case "validation_failed":
      return "activity-status activity-status-warning";

    case "operation_failed":
      return "activity-status activity-status-error";

    default:
      return "activity-status";
  }
};

const getReliabilityLabel = (score) => {
  if (score === null || score === undefined) {
    return "Not evaluated";
  }

  if (score >= 0.9) {
    return "High confidence";
  }

  if (score >= 0.7) {
    return "Moderate confidence";
  }

  return "Low confidence";
};

function ActivityPage() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const fetchActivity = useCallback(async (isRefresh = false) => {
    try {
      setError("");

      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      const response = await fetch(`${API_URL}/activity/?limit=100`);

      if (!response.ok) {
        throw new Error("Unable to load activity.");
      }

      const data = await response.json();

      setActivities(
        Array.isArray(data.activities) ? data.activities : []
      );
    } catch (err) {
      setError(err.message || "Unable to load activity.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchActivity();
  }, [fetchActivity]);

  const stats = useMemo(() => {
    const successful = activities.filter(
      (activity) => activity.success
    ).length;

    const failed = activities.length - successful;

    const evaluated = activities.filter(
      (activity) =>
        typeof activity.reliability_score === "number"
    );

    const averageReliability =
      evaluated.length > 0
        ? evaluated.reduce(
            (total, activity) =>
              total + activity.reliability_score,
            0
          ) / evaluated.length
        : null;

    return {
      total: activities.length,
      successful,
      failed,
      averageReliability,
    };
  }, [activities]);

  return (
    <div className="operations-page activity-page">
      <div className="operations-heading">
        <div>
          <div className="page-eyebrow">
            <Activity size={12} />
            Agent Activity
          </div>

          <h1>Activity</h1>

          <p>
            Audit trail for AI-driven payment operations and
            reliability checks.
          </p>
        </div>

        <button
          className="operations-refresh-button"
          onClick={() => fetchActivity(true)}
          disabled={loading || refreshing}
        >
          <RefreshCcw
            size={13}
            className={refreshing ? "activity-spin" : ""}
          />

          {refreshing ? "Refreshing" : "Refresh"}
        </button>
      </div>

      <div className="operations-stats activity-stats">
        <div className="operation-stat-card">
          <div className="operation-stat-icon">
            <Activity size={16} />
          </div>

          <span>Total operations</span>
          <strong>{stats.total}</strong>
        </div>

        <div className="operation-stat-card">
          <div className="operation-stat-icon">
            <CheckCircle2 size={16} />
          </div>

          <span>Successful</span>
          <strong>{stats.successful}</strong>
        </div>

        <div className="operation-stat-card">
          <div className="operation-stat-icon">
            <ShieldCheck size={16} />
          </div>

          <span>Avg. reliability</span>

          <strong>
            {stats.averageReliability === null
              ? "—"
              : `${Math.round(
                  stats.averageReliability * 100
                )}%`}
          </strong>
        </div>
      </div>

      <section className="panel operations-table-panel activity-panel">
        <div className="panel-header">
          <div>
            <span className="panel-eyebrow">
              Execution log
            </span>

            <h2>Recent operations</h2>
          </div>

          <span className="activity-count">
            {activities.length}{" "}
            {activities.length === 1
              ? "operation"
              : "operations"}
          </span>
        </div>

        {loading ? (
          <div className="operations-state">
            <div className="operations-spinner" />

            <strong>Loading activity</strong>

            <span>
              Fetching the latest agent operations.
            </span>
          </div>
        ) : error ? (
          <div className="operations-state operations-state-error">
            <div className="operations-state-icon">
              <XCircle size={18} />
            </div>

            <strong>Could not load activity</strong>

            <span>{error}</span>

            <button
              className="operations-state-button"
              onClick={() => fetchActivity()}
            >
              Try again
            </button>
          </div>
        ) : activities.length === 0 ? (
          <div className="operations-state">
            <div className="operations-state-icon">
              <Bot size={18} />
            </div>

            <strong>No agent activity yet</strong>

            <span>
              Operations executed through the AI Agent will
              appear here with their status and reliability
              result.
            </span>
          </div>
        ) : (
          <div className="activity-list">
            {activities.map((activity) => (
              <div
                className="activity-row"
                key={activity.id}
              >
                <div className="activity-operation-icon">
                  {activity.success ? (
                    <CheckCircle2 size={15} />
                  ) : (
                    <XCircle size={15} />
                  )}
                </div>

                <div className="activity-main">
                  <div className="activity-title-row">
                    <strong>
                      {formatOperation(
                        activity.operation
                      )}
                    </strong>

                    <span
                      className={getStatusClass(
                        activity.status
                      )}
                    >
                      <span />

                      {activity.status.replaceAll(
                        "_",
                        " "
                      )}
                    </span>
                  </div>

                  <p>{activity.user_query}</p>

                  <div className="activity-meta">
                    <span>
                      <Clock3 size={11} />
                      {formatDate(activity.timestamp)}
                    </span>

                    <span>
                      Operation ID: {activity.id}
                    </span>
                  </div>
                </div>

                <div className="activity-reliability">
                  <span>Reliability</span>

                  <strong>
                    {typeof activity.reliability_score ===
                    "number"
                      ? `${Math.round(
                          activity.reliability_score * 100
                        )}%`
                      : "—"}
                  </strong>

                  <small>
                    {getReliabilityLabel(
                      activity.reliability_score
                    )}
                  </small>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default ActivityPage;
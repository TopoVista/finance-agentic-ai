import { TransactionForm } from "@/components/transaction-form";
import { serverApiFetch } from "@/lib/api";

export default async function TransactionsPage() {
  const response = await serverApiFetch<any>("/transaction/all?pageSize=20&pageNumber=1");

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-semibold">Transactions</h2>
        <p className="mt-1 text-sm text-muted">Create and review income and expense records.</p>
      </div>
      <TransactionForm />
      <section className="rounded-md border border-border bg-panel p-4">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold">All transactions</h3>
          <span className="text-sm text-muted">{response.pagination.totalCount} total</span>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-muted">
                <th className="px-2 py-2">Date</th>
                <th className="px-2 py-2">Title</th>
                <th className="px-2 py-2">Category</th>
                <th className="px-2 py-2">Type</th>
                <th className="px-2 py-2">Payment</th>
                <th className="px-2 py-2">Amount</th>
              </tr>
            </thead>
            <tbody>
              {response.transactions.map((transaction: any) => (
                <tr key={transaction.id} className="border-b border-border/60">
                  <td className="px-2 py-3">{new Date(transaction.date).toLocaleDateString()}</td>
                  <td className="px-2 py-3">{transaction.title}</td>
                  <td className="px-2 py-3">{transaction.category}</td>
                  <td className="px-2 py-3">{transaction.type}</td>
                  <td className="px-2 py-3">{transaction.paymentMethod}</td>
                  <td className="px-2 py-3">${Number(transaction.amount).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

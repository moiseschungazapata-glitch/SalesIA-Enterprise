function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h2>SalesIA</h2>
        <span>Enterprise</span>
      </div>

      <nav className="sidebar-nav">
        <a href="#">Dashboard</a>
        <a href="#">Clientes</a>
        <a href="#">Productos</a>
        <a href="#">Ventas</a>
        <a href="#">Inventario</a>
        <a href="#">Analytics</a>
        <a href="#">Probabilidad</a>
        <a href="#">Insights</a>
        <a href="#">Reportes</a>
      </nav>
    </aside>
  )
}

export default Sidebar
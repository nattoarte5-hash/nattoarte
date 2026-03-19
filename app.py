import streamlit as st
import pandas as pd
import os
from datetime import date, datetime

st.set_page_config(page_title="Pedidos", layout="wide")

st.title("📦 Gestión de pedidos")

archivo_csv = "pedidos.csv"

# Crear archivo si no existe
if not os.path.exists(archivo_csv):
    df = pd.DataFrame(columns=[
        "Fecha", "Fecha Límite", "Cliente", "N° Orden",
        "Producto", "Tipo", "Cantidad Retratos",
        "Mascota", "Forma de Entrega", "Ubicación",
        "Estado", "Precio", "Observaciones"
    ])
    df.to_csv(archivo_csv, index=False)

df = pd.read_csv(archivo_csv)

productos = ["Mate", "Taza", "Cuadro", "Funda"]

formas_entrega = [
    "Retiro Ramos Mejía",
    "Envío Correo Sucursal",
    "Envío Correo Domicilio",
    "Moto"
]

tab1, tab2 = st.tabs(["📦 Pedidos", "📊 Estadísticas"])

# =====================
# 📦 PEDIDOS
# =====================
with tab1:

    # ALERTAS
    st.subheader("🔔 Alertas")

    hoy = datetime.today().date()

    for i, row in df.iterrows():
        try:
            fecha_limite = pd.to_datetime(row["Fecha Límite"]).date()
            dias = (fecha_limite - hoy).days

            if 0 <= dias <= 5:
                st.warning(f"⚠️ {row['Cliente']} vence en {dias} días")
            elif dias < 0:
                st.error(f"🚨 VENCIDO: {row['Cliente']}")
        except:
            pass

    # NUEVO PEDIDO
    st.subheader("➕ Nuevo pedido")

    with st.form("form"):
        col1, col2 = st.columns(2)

        with col1:
            fecha = st.date_input("Fecha", value=date.today())
            fecha_limite = st.date_input("Fecha límite")
            cliente = st.text_input("Cliente")
            orden = st.text_input("N° Orden")
            producto = st.selectbox("Producto", productos)
            tipo = st.text_input("Tipo / Modelo")

        with col2:
            cantidad = st.number_input("Cantidad", min_value=1)
            mascota = st.text_input("Mascota")
            entrega = st.selectbox("Entrega", formas_entrega)

            if entrega != "Retiro Ramos Mejía":
                ubicacion = st.text_input("Ubicación")
            else:
                ubicacion = ""

            estado = st.selectbox("Estado", ["Pendiente", "Hecho", "Despachado", "Entregado"])
            precio = st.number_input("Precio", min_value=0)
            observaciones = st.text_area("Observaciones")

        guardar = st.form_submit_button("Guardar")

    if guardar:
        nuevo = pd.DataFrame([[fecha, fecha_limite, cliente, orden,
                               producto, tipo, cantidad,
                               mascota, entrega, ubicacion,
                               estado, precio, observaciones]],
                             columns=df.columns)

        df = pd.concat([df, nuevo], ignore_index=True)
        df.to_csv(archivo_csv, index=False)
        st.success("Guardado 💾")

    # =====================
    # 📱 TARJETAS
    # =====================
    st.subheader("📋 Pedidos")

    for i, row in df.iterrows():

        try:
            fecha_limite = pd.to_datetime(row["Fecha Límite"]).date()
            dias = (fecha_limite - hoy).days
        except:
            dias = None

        # COLOR POR URGENCIA
        if dias is not None:
            if dias < 0:
                color = "#ffb3b3"
            elif dias <= 5:
                color = "#ffe0b3"
            else:
                color = "#e6f7ff"
        else:
            color = "#ffffff"

        st.markdown(f"""
        <div style="
            background-color:{color};
            padding:15px;
            border-radius:15px;
            margin-bottom:10px;
            box-shadow:2px 2px 10px rgba(0,0,0,0.1)
        ">
        <b>👤 {row['Cliente']}</b><br>
        🧾 Orden: {row['N° Orden']}<br>
        📦 {row['Producto']} - {row['Tipo']}<br>
        🐶 {row['Mascota']}<br>
        🚚 {row['Forma de Entrega']} ({row['Ubicación']})<br>
        💰 ${row['Precio']}<br>
        📅 Límite: {row['Fecha Límite']}<br>
        📌 Estado: <b>{row['Estado']}</b><br>
        📝 {row['Observaciones']}
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        # ENTREGADO
        if col1.button(f"✅ Entregado {i}"):
            df.at[i, "Estado"] = "Entregado"
            df.to_csv(archivo_csv, index=False)
            st.rerun()

        # ELIMINAR
        if col2.button(f"🗑️ Eliminar {i}"):
            df = df.drop(i)
            df.to_csv(archivo_csv, index=False)
            st.rerun()

        # EDITAR
        if col3.button(f"✏️ Editar {i}"):
            st.session_state["editar_idx"] = i

    # FORM EDITAR
    if "editar_idx" in st.session_state:
        i = st.session_state["editar_idx"]
        row = df.loc[i]

        st.subheader("✏️ Editar pedido")

        with st.form("editar_form"):
            cliente = st.text_input("Cliente", row["Cliente"])
            orden = st.text_input("Orden", row["N° Orden"])
            producto = st.selectbox("Producto", productos, index=productos.index(row["Producto"]))
            tipo = st.text_input("Tipo", row["Tipo"])

            cantidad = st.number_input("Cantidad", value=int(row["Cantidad Retratos"]))
            mascota = st.text_input("Mascota", row["Mascota"])

            estado = st.selectbox(
                "Estado",
                ["Pendiente", "Hecho", "Despachado", "Entregado"],
                index=["Pendiente", "Hecho", "Despachado", "Entregado"].index(row["Estado"])
            )

            precio = st.number_input("Precio", value=int(row["Precio"]))
            observaciones = st.text_area("Observaciones", row["Observaciones"])

            guardar = st.form_submit_button("Guardar cambios")

            if guardar:
                df.loc[i, "Cliente"] = cliente
                df.loc[i, "N° Orden"] = orden
                df.loc[i, "Producto"] = producto
                df.loc[i, "Tipo"] = tipo
                df.loc[i, "Cantidad Retratos"] = cantidad
                df.loc[i, "Mascota"] = mascota
                df.loc[i, "Estado"] = estado
                df.loc[i, "Precio"] = precio
                df.loc[i, "Observaciones"] = observaciones

                df.to_csv(archivo_csv, index=False)
                st.success("Actualizado ✅")
                del st.session_state["editar_idx"]
                st.rerun()

# =====================
# 📊 ESTADÍSTICAS
# =====================
with tab2:
    st.subheader("💰 Total ganado")
    st.write(f"${df['Precio'].sum()}")

    st.subheader("📦 Productos vendidos")
    st.bar_chart(df["Producto"].value_counts())

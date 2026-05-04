import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import datetime as dt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['figure.dpi'] = 130
plt.rcParams['font.family'] = 'DejaVu Sans'
COLORS = {
    'primary':   '#2D6A4F',
    'secondary': '#40916C',
    'accent':    '#74C69D',
    'light':     '#B7E4C7',
    'danger':    '#E63946',
    'warning':   '#F4A261',
    'info':      '#457B9D',
    'dark':      '#1B4332',
}


# 0. LOAD & CLEANING DATA=

df = pd.read_csv(
    'data_praktikum_analisis_data_-_data_praktikum_analisis_data.csv'
)

print("=" * 55)
print("  ANALISIS PERFORMA PENJUALAN E-COMMERCE 2023")
print("=" * 55)
print(f"\n[INFO] Total baris awal     : {len(df)}")

df['Order_Date'] = pd.to_datetime(df['Order_Date'])
df = df.dropna(subset=['Total_Sales'])
df = df[df['Price_Per_Unit'] > 0]
df['Month'] = df['Order_Date'].dt.to_period('M').astype(str)

print(f"[INFO] Total baris bersih   : {len(df)}")
print(f"[INFO] Pelanggan unik       : {df['CustomerID'].nunique()}")
print(f"[INFO] Kategori produk      : {df['Product_Category'].nunique()}")
print(f"[INFO] Total Pendapatan     : Rp {df['Total_Sales'].sum():,.0f}")
print()


# 1. TREN PENJUALAN BULANAN

monthly = df.groupby('Month')['Total_Sales'].sum().reset_index()
monthly.columns = ['Bulan', 'Total_Sales']
peak_idx = monthly['Total_Sales'].idxmax()

fig, ax = plt.subplots(figsize=(12, 5))
bars = ax.bar(monthly['Bulan'], monthly['Total_Sales'],
              color=COLORS['accent'], edgecolor=COLORS['primary'], linewidth=0.8)
bars[peak_idx].set_color(COLORS['primary'])

ax.axhline(monthly['Total_Sales'].mean(), color=COLORS['danger'],
           linestyle='--', linewidth=1.4, label=f"Rata-rata: Rp {monthly['Total_Sales'].mean():,.0f}")

# label nilai bar
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 300_000,
            f"Rp {bar.get_height()/1_000_000:.1f}M",
            ha='center', va='bottom', fontsize=7.5, color=COLORS['dark'])

ax.set_title('📈 Tren Penjualan Bulanan — 2023', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Bulan', fontsize=10)
ax.set_ylabel('Total Penjualan (Rp)', fontsize=10)
ax.tick_params(axis='x', rotation=45)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'Rp {x/1e6:.0f}M'))
ax.legend(fontsize=9)
ax.grid(axis='y', alpha=0.3)
sns.despine()
plt.tight_layout()
plt.savefig('01_tren_penjualan_bulanan.png')
plt.close()
print("[✓] Grafik 1 — Tren Penjualan Bulanan tersimpan.")


# 2. HEATMAP KORELASI

corr_cols = ['Quantity', 'Price_Per_Unit', 'Ad_Budget', 'Total_Sales']
corr_matrix = df[corr_cols].corr()

fig, ax = plt.subplots(figsize=(7, 5.5))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='YlGn',
            mask=mask, ax=ax, linewidths=0.5,
            annot_kws={'size': 11, 'weight': 'bold'},
            cbar_kws={'shrink': 0.8})
ax.set_title('🔥 Heatmap Korelasi Antar Variabel', fontsize=13, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig('02_korelasi_heatmap.png')
plt.close()
print("[✓] Grafik 2 — Heatmap Korelasi tersimpan.")


# TUGAS 1 — SCATTER PLOT UNDERPERFORMER

avg_price = df['Price_Per_Unit'].mean()
category_stats = df.groupby('Product_Category').agg(
    Avg_Price=('Price_Per_Unit', 'mean'),
    Total_Qty=('Quantity', 'sum')
).reset_index()

fig, ax = plt.subplots(figsize=(9, 6))
palette = [COLORS['danger'] if (row.Avg_Price > avg_price and row.Total_Qty == category_stats['Total_Qty'].min())
           else COLORS['warning'] if row.Total_Qty < category_stats['Total_Qty'].median()
           else COLORS['secondary']
           for _, row in category_stats.iterrows()]

scatter = ax.scatter(category_stats['Avg_Price'], category_stats['Total_Qty'],
                     s=category_stats['Total_Qty']*8,
                     c=palette, edgecolors=COLORS['dark'], linewidths=0.8, alpha=0.9, zorder=3)

for _, row in category_stats.iterrows():
    ax.annotate(row['Product_Category'],
                xy=(row['Avg_Price'], row['Total_Qty']),
                xytext=(8, 5), textcoords='offset points',
                fontsize=9.5, fontweight='bold', color=COLORS['dark'])

ax.axvline(avg_price, color=COLORS['danger'], linestyle='--', linewidth=1.2, alpha=0.7,
           label=f'Rata-rata Harga: Rp {avg_price:,.0f}')

# Legend
legend_handles = [
    mpatches.Patch(color=COLORS['danger'],   label='🔴 Underperformer (Harga tinggi, Qty rendah)'),
    mpatches.Patch(color=COLORS['warning'],  label='⚠️  Perlu perhatian'),
    mpatches.Patch(color=COLORS['secondary'],label='✅  Normal'),
]
ax.legend(handles=legend_handles, fontsize=8.5, loc='upper right')

ax.set_title('🎯 Tugas 1 — Scatter Plot: Harga vs Volume Penjualan per Kategori',
             fontsize=12, fontweight='bold', pad=12)
ax.set_xlabel('Rata-rata Harga per Unit (Rp)', fontsize=10)
ax.set_ylabel('Total Quantity Terjual', fontsize=10)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'Rp {x/1e3:.0f}K'))
ax.grid(alpha=0.3)
sns.despine()
plt.tight_layout()
plt.savefig('03_underperformer_scatter.png')
plt.close()
print("[✓] Grafik 3 — Scatter Underperformer tersimpan.")

# Print tabel
print("\n[TUGAS 1] Identifikasi Underperformer:")
category_stats['Status'] = category_stats.apply(
    lambda r: '🔴 Underperformer' if (r.Avg_Price > avg_price and r.Total_Qty == category_stats['Total_Qty'].min())
    else '⚠️  Perlu Perhatian' if r.Total_Qty < category_stats['Total_Qty'].median()
    else '✅  Normal', axis=1
)
print(category_stats.sort_values('Total_Qty').to_string(index=False))


# TUGAS 2 — RFM ANALYSIS

snapshot_date = df['Order_Date'].max() + dt.timedelta(days=1)
rfm = df.groupby('CustomerID').agg(
    Recency  = ('Order_Date', lambda x: (snapshot_date - x.max()).days),
    Frequency= ('Order_ID',   'count'),
    Monetary = ('Total_Sales','sum')
).reset_index()

rfm['R_Score'] = pd.qcut(rfm['Recency'],   5, labels=[5, 4, 3, 2, 1])
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
rfm['M_Score'] = pd.qcut(rfm['Monetary'],  5, labels=[1, 2, 3, 4, 5])
rfm['RFM_Score'] = (rfm['R_Score'].astype(int) +
                    rfm['F_Score'].astype(int) +
                    rfm['M_Score'].astype(int))

def segmentasi(score):
    if score >= 13: return 'Champions'
    elif score >= 10: return 'Loyal'
    elif score >= 7:  return 'At Risk'
    else:             return 'Lost'

rfm['Segment'] = rfm['RFM_Score'].apply(segmentasi)

seg_count = rfm['Segment'].value_counts().reindex(['Champions','Loyal','At Risk','Lost'])
seg_colors = [COLORS['primary'], COLORS['secondary'], COLORS['warning'], COLORS['danger']]

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Pie chart
wedges, texts, autotexts = axes[0].pie(
    seg_count, labels=seg_count.index, autopct='%1.1f%%',
    colors=seg_colors, startangle=140,
    wedgeprops={'edgecolor': 'white', 'linewidth': 2},
    textprops={'fontsize': 10})
for at in autotexts:
    at.set_fontweight('bold')
axes[0].set_title('Distribusi Segmen Pelanggan', fontsize=11, fontweight='bold')

# Bar chart monetary per segment
seg_monetary = rfm.groupby('Segment')['Monetary'].mean().reindex(['Champions','Loyal','At Risk','Lost'])
bars = axes[1].barh(seg_monetary.index, seg_monetary.values,
                    color=seg_colors, edgecolor=COLORS['dark'], linewidth=0.7)
for bar, val in zip(bars, seg_monetary.values):
    axes[1].text(val + 200_000, bar.get_y() + bar.get_height()/2,
                 f'Rp {val/1e6:.2f}M', va='center', fontsize=9, fontweight='bold')
axes[1].set_title('Rata-rata Monetary per Segmen', fontsize=11, fontweight='bold')
axes[1].set_xlabel('Rata-rata Total Belanja (Rp)')
axes[1].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'Rp {x/1e6:.1f}M'))
axes[1].grid(axis='x', alpha=0.3)
sns.despine(ax=axes[1])

fig.suptitle('👥 Tugas 2 — Segmentasi Pelanggan (RFM Analysis)', fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('04_rfm_segmentasi.png', bbox_inches='tight')
plt.close()
print("\n[✓] Grafik 4 — RFM Segmentasi tersimpan.")
print(f"\n[TUGAS 2] Hasil RFM Segmentasi ({len(rfm)} pelanggan):")
print(seg_count.to_string())


# TUGAS 3 — EFISIENSI KATEGORI

cat_eff = df.groupby('Product_Category').agg(
    Revenue  =('Total_Sales','sum'),
    Ad_Budget=('Ad_Budget','sum')
).reset_index()
cat_eff['ROI'] = cat_eff['Revenue'] / cat_eff['Ad_Budget']
cat_eff = cat_eff.sort_values('ROI')  # dari paling tidak efisien ke efisien

bar_colors = [COLORS['danger'] if r < 1.1 else
              COLORS['warning'] if r < 1.3 else
              COLORS['secondary'] for r in cat_eff['ROI']]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(cat_eff['Product_Category'], cat_eff['ROI'],
               color=bar_colors, edgecolor=COLORS['dark'], linewidth=0.7, height=0.55)
ax.axvline(1.0, color=COLORS['danger'], linestyle='--', linewidth=1.2,
           label='Break-even (ROI = 1.0×)')
for bar, val in zip(bars, cat_eff['ROI']):
    ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
            f'{val:.2f}×', va='center', fontsize=10, fontweight='bold')
ax.set_title('📊 Tugas 3 — Efisiensi Kategori Produk\n(ROI = Revenue / Ad Budget)',
             fontsize=12, fontweight='bold', pad=12)
ax.set_xlabel('Return on Investment (ROI)', fontsize=10)
ax.legend(fontsize=9)
ax.grid(axis='x', alpha=0.3)
sns.despine()
plt.tight_layout()
plt.savefig('05_efisiensi_kategori.png')
plt.close()
print("\n[✓] Grafik 5 — Efisiensi Kategori tersimpan.")
print("\n[TUGAS 3] ROI per Kategori:")
print(cat_eff[['Product_Category','Revenue','Ad_Budget','ROI']].to_string(index=False))

# TUGAS 4 — UJI HIPOTESIS

median_ad = df['Ad_Budget'].median()
high_ad = df[df['Ad_Budget'] >  median_ad]['Total_Sales']
low_ad  = df[df['Ad_Budget'] <= median_ad]['Total_Sales']
t_stat, p_value = stats.ttest_ind(high_ad, low_ad)

fig, ax = plt.subplots(figsize=(8, 5))
bp = ax.boxplot([high_ad, low_ad],
                patch_artist=True,
                labels=[f'Iklan Tinggi\n(> Rp {median_ad/1e3:.0f}K)',
                        f'Iklan Rendah\n(≤ Rp {median_ad/1e3:.0f}K)'],
                medianprops=dict(color=COLORS['danger'], linewidth=2),
                whiskerprops=dict(color=COLORS['dark']),
                capprops=dict(color=COLORS['dark']),
                flierprops=dict(marker='o', color=COLORS['warning'], alpha=0.5))
bp['boxes'][0].set_facecolor(COLORS['light'])
bp['boxes'][1].set_facecolor(COLORS['accent'])

ax.set_title(f'🔬 Tugas 4 — Uji Hipotesis: Pengaruh Anggaran Iklan\n'
             f'p-value = {p_value:.4f} | {"H₀ Diterima (Tidak Signifikan)" if p_value > 0.05 else "H₁ Diterima (Signifikan)"}',
             fontsize=11, fontweight='bold', pad=12)
ax.set_ylabel('Total Penjualan (Rp)', fontsize=10)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'Rp {x/1e6:.1f}M'))

mean_high = high_ad.mean()
mean_low  = low_ad.mean()
ax.text(1, ax.get_ylim()[1]*0.92, f'Rata-rata:\nRp {mean_high/1e6:.2f}M',
        ha='center', fontsize=9, color=COLORS['info'], fontweight='bold')
ax.text(2, ax.get_ylim()[1]*0.92, f'Rata-rata:\nRp {mean_low/1e6:.2f}M',
        ha='center', fontsize=9, color=COLORS['info'], fontweight='bold')
ax.grid(axis='y', alpha=0.3)
sns.despine()
plt.tight_layout()
plt.savefig('06_uji_hipotesis_boxplot.png')
plt.close()
print("\n[✓] Grafik 6 — Uji Hipotesis Boxplot tersimpan.")
print(f"\n[TUGAS 4] Uji T-Test Independen:")
print(f"  Rata-rata Iklan Tinggi : Rp {mean_high:,.0f}")
print(f"  Rata-rata Iklan Rendah : Rp {mean_low:,.0f}")
print(f"  t-statistic            : {t_stat:.4f}")
print(f"  p-value                : {p_value:.4f}")
print(f"  Kesimpulan             : {'H₀ Diterima — Tidak ada perbedaan signifikan' if p_value > 0.05 else 'H₁ Diterima — Ada perbedaan signifikan'}")

# TUGAS 5 — REGRESI LINEAR

X = df[['Ad_Budget']]
y = df['Total_Sales']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)
r2 = model.score(X_test, y_test)
coef = model.coef_[0]
intercept = model.intercept_

X_line = np.linspace(df['Ad_Budget'].min(), df['Ad_Budget'].max(), 200).reshape(-1,1)
y_line = model.predict(X_line)

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.scatter(X_test, y_test, color=COLORS['accent'], edgecolor=COLORS['dark'],
           alpha=0.8, s=55, label='Data Uji', zorder=3)
ax.scatter(X_train, y_train, color=COLORS['light'], edgecolor=COLORS['dark'],
           alpha=0.5, s=40, label='Data Latih', zorder=2)
ax.plot(X_line, y_line, color=COLORS['danger'], linewidth=2,
        label=f'Garis Regresi\ny = {coef:.2f}x + {intercept:,.0f}')

ax.set_title(f'📉 Tugas 5 — Regresi Linear: Ad Budget → Total Sales\n'
             f'R² = {r2:.4f} | Koefisien = {coef:.4f}',
             fontsize=11, fontweight='bold', pad=12)
ax.set_xlabel('Anggaran Iklan / Ad Budget (Rp)', fontsize=10)
ax.set_ylabel('Total Penjualan (Rp)', fontsize=10)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'Rp {x/1e6:.1f}M'))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'Rp {x/1e6:.1f}M'))
ax.legend(fontsize=9)
ax.grid(alpha=0.3)
sns.despine()
plt.tight_layout()
plt.savefig('07_regresi_linear.png')
plt.close()
print("\n[✓] Grafik 7 — Regresi Linear tersimpan.")
print(f"\n[TUGAS 5] Regresi Linear:")
print(f"  Koefisien Iklan (β₁)  : {coef:.4f}")
print(f"  Intercept (β₀)        : Rp {intercept:,.0f}")
print(f"  R² Score (Test Set)   : {r2:.4f}")

print("\n" + "=" * 55)
print("  SEMUA ANALISIS SELESAI — 7 GRAFIK TERSIMPAN ✓")
print("=" * 55)
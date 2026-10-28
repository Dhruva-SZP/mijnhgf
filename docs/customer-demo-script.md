# Gridbricks Customer Presentation Script: UK Day-Ahead Wind Procurement

**Target Audience:** Energy Procurement & Trading Team, UK Electricity Utility  
**Presenter Role:** Senior Full-Stack Software Engineer & Energy Analytics Lead  
**Format:** Live Video Pitch / Demonstration  
**Duration Target:** Strictly under 5:00 minutes (Part 1 of Challenge Submission)

---

### [0:00 - 0:45] Minute 1: The Commercial Challenge & Value Proposition

> *"Good morning, everyone. Thank you for joining this demonstration of the Gridbricks Wind Procurement Analytics Platform.*
>
> *As UK electricity retailers and commercial procurement managers, your core mandate is purchasing wholesale power to meet customer demand at the lowest possible cost while hedging volatile market exposure.*
>
> *Every day, by 11:00 AM on day D-1, your team must commit to purchase volumes in the GB Day-Ahead wholesale auctions on EPEX SPOT or Nord Pool. To decide how much thermal and baseload power to procure, you rely heavily on National Grid's renewable forecasts—especially wind.*
>
> *When forecasts are wrong, the financial penalty is severe. If wind underperforms, you are left short and forced to buy emergency power in the Balancing Mechanism at punitive cash-out prices. If wind overperforms, you are long and must sell surplus power at distressingly low or negative prices.*
>
> *Today, I am proud to present our pilot solution: a high-fidelity analytics platform that turns raw Elexon BMRS data into actionable procurement intelligence, benchmarked across the full January 2026 delivery window."*

---

### [0:45 - 2:00] Minute 2: Executive Overview & Accuracy KPIs

*(Screen share: Pointing to Executive Overview KPI cards)*

> *"Let’s look at the executive dashboard for January 2026—a month characterized by multiple high-wind winter storm fronts.*
>
> *Over the 1,488 half-hour settlement periods in January, total actual wind generation reached **2.42 Terawatt-hours (TWh)**, with an average output of **3,252 MW**.*
>
> *Now, look at our accuracy metrics on the top row:*
> 1. *Our **Weighted Absolute Percentage Error (WAPE)** stands at **18.36%**. WAPE is the gold-standard metric for power trading desks because it weights errors by volume, protecting us from distortion during low-wind periods.*
> 2. *Our **Mean Absolute Error (MAE)** is **2,126 MW**, with a Root Mean Squared Error of **2,620 MW**.*
> 3. *Most importantly for your trading strategy: look at the **Forecast Bias** card. It displays **+1,840 MW**.*
>
> *What does a systematic positive bias tell your procurement desk? It proves that day-ahead wind forecasts during January 2026 were consistently **over-estimating** wind generation. If your team bought thermal power assuming the forecast was unbiased, you would have routinely under-hedged and found yourself short on delivery day. Armed with this metric, your traders can apply an empirical derating factor to day-ahead bids, saving hundreds of thousands of pounds in imbalance settlement fees."*

---

### [2:00 - 3:15] Minute 3: Actual vs Forecast Interactive Chart & D-1 Cutoff Sensitivity

*(Screen share: Interacting with Time-Series Chart, zooming into Storm Week Jan 1-7, toggling D-1 Cutoff)*

> *"Moving down to our interactive dispatch visualizer: the solid green line shows genuine half-hourly wind actuals from Elexon FUELHH, while the blue dashed line shows the active day-ahead forecast selected from WINDFOR.*
>
> *Notice our Discrepancy Band feature. During the storm peaks of January 2nd and 3rd, wind generation exceeded 15,000 MW. Our tooltips show you the exact delivery half-hour, the forecast version used, and the signed imbalance in megawatts.*
>
> *Now, notice the **D-1 Cutoff control** in the top navigation. By default, it is locked to **11:00 UTC on day D-1**, reflecting the EPEX SPOT day-ahead auction gate closure. Our engine prevents any future data leakage—meaning your traders only see forecasts that were physically published and available before bidding closed.*
>
> *If your desk also trades the secondary 12:00 UTC window or the 17:00 UTC day-ahead gate closure, watch what happens when I switch the cutoff to 17:00 UTC: WAPE immediately drops from 18.36% down to 17.14%. This gives your desk clear quantitative evidence of the financial value of delaying hedges to later trading windows when weather models update."*

---

### [3:15 - 4:15] Minute 4: Error Distribution & Largest Risk Settlement Intervals

*(Screen share: Switching to the Error Analysis section and Largest Errors tab)*

> *"Next, let’s inspect the **Forecast Error Analysis** section.*
>
> *The distribution histogram proves our findings: the error distribution is right-skewed, showing frequent 1,500 to 5,000 MW over-forecast errors.*
>
> *When we click on the **Largest Errors** tab, the system automatically isolates the 10 most extreme forecast misalignments of the month.*
> *For example, on January 3rd, the day-ahead forecast called for over 15,000 MW, but actual generation fell short by more than 3,400 MW. The platform flags this as a **SURPLUS / DEFICIT RISK** and explains the commercial implication: the desk was short and exposed to cash-out penalties.*
>
> *Below that, our **Detailed Settlement Table** gives your quantitative analysts complete access to all 1,488 settlement intervals, with instant search, sorting, and single-click **CSV Export** for your trade capture and ETRM systems."*

---

### [4:15 - 5:00] Minute 5: Commercial Impact & Summary

> *"In summary, the Gridbricks platform delivers three immediate advantages to your procurement operations:*
>
> 1. * **Total Market Realism:** Defensible forecast selection at the exact 11:00 UTC day-ahead auction cutoff, with zero future data contamination.*
> 2. * **Quantified Error Buffers:** Clear MAE, Bias, and WAPE metrics that allow your traders to de-risk volume commitments and avoid cash-out penalties.*
> 3. * **Audited Data Integrity:** 100% genuine Elexon BMRS data with full local offline caching and complete publication version tracking.*
>
> *We are excited to partner with your utility to roll this system out across your real-time trading desks. Thank you, and I look forward to your questions."*

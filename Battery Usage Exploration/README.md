<h2>Graphing battery change during trips</h2>
Using [battPerTripVer2.py](battPerTripVer2.py)

![Graph1](./images/slide4_car6.png)

![Graph2](./images/slide5_car3.png)

![Graph3](./images/slide5_car8.png)

<h2>Graphing battery change per car</h2>

![Graph4](./images/slide8_car6.png)

![Graph5](./images/slide9_car8.png)

<h2>Battery percentage increase after every charge</h2>
In the first graph, I noticed there were a lot of charges in the <10% bin. Looking into the data, there were a lot of charges recorded to have a battery change of 0% or 1%, which are clear errors.
![Bins1](./images/bins_withUnder3.png)

This graph removes any charges that have a battery percentage difference of <3%.
![Bins2](./images/bins_withoutUnder3.png)

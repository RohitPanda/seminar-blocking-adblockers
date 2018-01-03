set size 1,.7
set terminal pdfcairo enhanced font "Gill Sans,8" linewidth 4 rounded fontscale .750
set style line 80 lt rgb "#808080"
set style line 81 lt 0  # dashed
set style line 81 lt rgb "#808080"  # grey
set grid back linestyle 81
set border 3 back linestyle 80
set xtics nomirror
set ytics nomirror
set style line 1 lt rgb "#A00000" lw 2 pt -1 
set style line 2 lt rgb "#F25900" lw 2 pt -1 
set style line 3 lt rgb "#00A000" lw 2 pt -1 
set style line 4 lt rgb "#5060D0" lw 2 pt -1 
set style line 5 lt rgb "#A9A9A9" lw 2 pt -1 
set style line 6 lt rgb "#000000" lw 2 pt -1 
set output "./script-lengths-100.pdf" 
set xlabel "Script Length (characters)"
set ylabel "Cumulative Probability"
set key outside horizontal center top samplen 1 spacing 1 width -.5
set xrange [0:5000]
set yrange [0:1]
plot "./script-lengths-100" using ($2):($1) title "" w lp ls 1 

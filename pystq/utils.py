def LerpArray(x, y, t):
   i = 0
   while (i < (len(x) - 2) and t > x[i + 1]):
      i += 1
   return (y[i] * (x[i + 1] - t) + y[i + 1] * (t - x[i])) / (x[i + 1] - x[i])

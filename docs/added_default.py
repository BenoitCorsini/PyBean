from bean import Canvas

CV = Canvas()
CV.add_arg('--dpi', type=int, default=50)
CV.set_args()
print(CV.dpi)
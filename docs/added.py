from bean import Canvas

CV = Canvas()
CV.add_arg('--dpi', type=int)
CV.set_args()
print(CV.dpi)
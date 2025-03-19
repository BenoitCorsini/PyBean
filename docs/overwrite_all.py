from bean import Canvas

CV = Canvas(dpi=50)
CV.add_arg('--dpi', type=int, default=25)
CV.set_args()
print(CV.dpi)
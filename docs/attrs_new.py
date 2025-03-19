from bean import Canvas

CV = Canvas()
CV.add_arg('--gifsize')
CV.set_args()
print(
	hasattr(CV, 'figsize'),
	hasattr(CV, 'gifsize'),
)
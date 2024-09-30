
cpu:
	@if [ -z "$(TOKEN)" ]; then \
		echo "No token! Please set the TOKEN environment variable."; \
		exit 1; \
	fi
	curl -X POST https://mwufi--notebook-start.modal.run \
		-H "Authorization: Bearer $(TOKEN)" \
		-H "Content-Type: application/json" \
		-d '{"gpu_type": null}'

t4:
	@if [ -z "$(TOKEN)" ]; then \
		echo "No token! Please set the TOKEN environment variable."; \
		exit 1; \
	fi
	curl -X POST https://mwufi--notebook-start.modal.run \
		-H "Authorization: Bearer $(TOKEN)" \
		-H "Content-Type: application/json" \
		-d '{"gpu_type": "t4"}'

a100:
	@if [ -z "$(TOKEN)" ]; then \
		echo "No token! Please set the TOKEN environment variable."; \
		exit 1; \
	fi
	curl -X POST https://mwufi--notebook-start.modal.run \
		-H "Authorization: Bearer $(TOKEN)" \
		-H "Content-Type: application/json" \
		-d '{"gpu_type": "a100"}'

a10g:
	@if [ -z "$(TOKEN)" ]; then \
		echo "No token! Please set the TOKEN environment variable."; \
		exit 1; \
	fi
	curl -X POST https://mwufi--notebook-start.modal.run \
		-H "Authorization: Bearer $(TOKEN)" \
		-H "Content-Type: application/json" \
		-d '{"gpu_type": "a10g"}'
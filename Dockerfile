FROM public.ecr.aws/docker/library/python:3.11.11-alpine AS build

RUN <<eot
    set -ex

    addgroup -S ai-gen-commit
    adduser -S ai-gen-commit -u 1000
eot

USER ai-gen-commit

WORKDIR /home/ai-gen-commit

COPY --chown=ai-gen-commit:ai-gen-commit . .

RUN pip install --no-cache-dir --user .


FROM public.ecr.aws/docker/library/python:3.11.11-alpine

LABEL description="AI-generated commit message for your staged changes!"

RUN <<eot
    set -ex

    addgroup -S ai-gen-commit
    adduser -S ai-gen-commit -u 1000
eot

USER ai-gen-commit

WORKDIR /home/ai-gen-commit

ENV PATH=$PATH:/home/ai-gen-commit/.local/bin

COPY --from=build --chown=ai-gen-commit /home/ai-gen-commit/.local /home/ai-gen-commit/.local/

ENTRYPOINT [ "aic" ]

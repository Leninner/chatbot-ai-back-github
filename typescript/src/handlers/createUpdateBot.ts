import { APIGatewayProxyEventBase, APIGatewayProxyResult } from 'aws-lambda';
import middy from '@middy/core';
import httpHeaderNormalizer from '@middy/http-header-normalizer';
import httpErrorHandler from '@middy/http-error-handler';
import cors from '@middy/http-cors';
import { captureLambdaHandler } from '@aws-lambda-powertools/tracer';
import { logMetrics } from '@aws-lambda-powertools/metrics';
import { injectLambdaContext } from '@aws-lambda-powertools/logger';
import { logger, metrics, tracer } from '../common';

interface CreateBotRequest {
    name: string;
    description: string;
    botName: string;
    botRole: string;
    company: string;
}

const lambdaHandler = async (event: APIGatewayProxyEventBase<CreateBotRequest>): Promise<APIGatewayProxyResult> => {
    logger.info('[POST /bots] Create bot lambda invoked', {
        details: {
            ...event,
        },
    });
    tracer.putAnnotation('awsRequestId', event.requestContext.requestId);

    return {
        statusCode: 200,
        body: JSON.stringify({
            message: 'hello world',
        }),
    };
};

export const handler = middy(lambdaHandler)
    .use(captureLambdaHandler(tracer))
    .use(logMetrics(metrics, { captureColdStartMetric: true }))
    .use(injectLambdaContext(logger))
    .use(httpHeaderNormalizer())
    .use(httpErrorHandler())
    .use(cors());

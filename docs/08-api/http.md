# API HTTP

Base:

`/api/v1`

## Health

`GET /health`

## Storage

`GET /storage/devices`
`GET /storage/devices/{id}`

## Analysis

`POST /downloads/analyze`

```json
{
  "url": "https://..."
}
```

## Jobs

`POST /downloads`
`GET /downloads/{job_id}`
`POST /downloads/{job_id}/cancel`
`POST /downloads/{job_id}/resume`

## History

`GET /downloads/history`

La API debe usar DTOs Pydantic y nunca devolver directamente entidades ORM.

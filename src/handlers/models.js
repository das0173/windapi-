import { listModels } from '../models.js';

export function handleModels() {
  const models = listModels();
  return { 
    object: 'list', 
    data: models,
    has_more: false,
    first_id: models.length ? models[0].id : null,
    last_id: models.length ? models[models.length - 1].id : null,
  };
}

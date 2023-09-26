const { setTimeout } = require('timers/promises');
const dotenv = require('dotenv');
dotenv.config();

describe('toggleRequiredFieldsOnReviewForm', () => {
  beforeAll(async () => {
    await page.goto(
      `http://localhost:${process.env.DJANGO_PORT}/reads-app/reviews/new`,
    );
    await setTimeout(3000); // Wait for vue to be mounted
  });

  const isFieldRequired = async (field) => {
    return await (await field.getProperty('required')).jsonValue();
  };

  const getOptionValue = async (selectId, optionText) => {
    // Get the text value of an option from a select field.
    const option = await (
      await page.$x(`//*[@id = "${selectId}"]/option[text() = "${optionText}"]`)
    )[0];
    const optionValue = await (await option.getProperty('value')).jsonValue();
    return optionValue;
  };

  it('should toggle MediaItem form fields "required" attribute', async () => {
    const bookTitleField = await page.$('#id_book-title');
    const filmTitleField = await page.$('#id_film-title');
    const bookButton = (await page.$x('//span[text()="Book"]'))[0];
    const filmButton = (await page.$x('//span[text()="Film"]'))[0];
    const selectExistingButton = (await page.$x('//span[text()="Select Existing"]'))[0];
    const createNewButton = (await page.$x('//span[text()="Create New"]'))[0];

    // Should not be required on startup
    await expect(isFieldRequired(bookTitleField)).resolves.toBeFalsy();
    await expect(isFieldRequired(filmTitleField)).resolves.toBeFalsy();

    // Select existing book
    await bookButton.click();
    await selectExistingButton.click();
    await expect(isFieldRequired(bookTitleField)).resolves.toBeFalsy();
    await expect(isFieldRequired(filmTitleField)).resolves.toBeFalsy();

    // Create new book
    await createNewButton.click();
    await expect(isFieldRequired(bookTitleField)).resolves.toBeTruthy();
    await expect(isFieldRequired(filmTitleField)).resolves.toBeFalsy();

    // Create new film
    await filmButton.click();
    await expect(isFieldRequired(bookTitleField)).resolves.toBeFalsy();
    await expect(isFieldRequired(filmTitleField)).resolves.toBeTruthy();

    // Select existing film
    await selectExistingButton.click();
    await expect(isFieldRequired(bookTitleField)).resolves.toBeFalsy();
    await expect(isFieldRequired(filmTitleField)).resolves.toBeFalsy();
  });

  it('should toggle Strategy form fields "required" attribute', async () => {
    const strategySelect = await page.$('#id_review-strategy_content_type');
    const ebertOptionValue = await getOptionValue(
      'id_review-strategy_content_type',
      'Ebert',
    );
    const goodreadsOptionValue = await getOptionValue(
      'id_review-strategy_content_type',
      'Goodreads',
    );
    const maximusOptionValue = await getOptionValue(
      'id_review-strategy_content_type',
      'Maximus',
    );
    const ebertField = await page.$('#id_ebertstrategy-rating');
    const goodreadsField = await page.$('#id_goodreadsstrategy-stars');
    const maximusField = await page.$('#id_maximusstrategy-recommended_0');

    // Should not be required on startup
    await expect(isFieldRequired(ebertField)).resolves.toBeFalsy();
    await expect(isFieldRequired(goodreadsField)).resolves.toBeFalsy();
    await expect(isFieldRequired(maximusField)).resolves.toBeFalsy();

    // Ebert should be required if selected
    await strategySelect.select(ebertOptionValue);
    await expect(isFieldRequired(ebertField)).resolves.toBeTruthy();
    await expect(isFieldRequired(goodreadsField)).resolves.toBeFalsy();
    await expect(isFieldRequired(maximusField)).resolves.toBeFalsy();

    // Goodreads should be required if selected
    await strategySelect.select(goodreadsOptionValue);
    await expect(isFieldRequired(ebertField)).resolves.toBeFalsy();
    await expect(isFieldRequired(goodreadsField)).resolves.toBeTruthy();
    await expect(isFieldRequired(maximusField)).resolves.toBeFalsy();

    // Maximus should be required if selected
    await strategySelect.select(maximusOptionValue);
    await expect(isFieldRequired(ebertField)).resolves.toBeFalsy();
    await expect(isFieldRequired(goodreadsField)).resolves.toBeFalsy();
    await expect(isFieldRequired(maximusField)).resolves.toBeTruthy();
  });
});

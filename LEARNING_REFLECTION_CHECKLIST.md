# Learning Reflection Checklist

Answer these questions **in your own words** in a separate document or section. They are prompts only: no answers are provided here on purpose, because the reflection must reflect what *you* learned.

## Django models
- [ ] Why are `DecimalField`s used for weights, dimensions and cost instead of `FloatField`?
- [ ] What does `on_delete=models.PROTECT` on `OrderItem.product` do, and why was it chosen?
- [ ] What is the difference between a field validator and a database `CheckConstraint`? Why have both?
- [ ] What does `related_name="items"` give you, and how is the order total calculated?

## Forms and validation
- [ ] What happens when a `ModelForm` is submitted with invalid data, and where do the error messages come from?
- [ ] How does an inline formset let one page create an order and several order items at once?
- [ ] Why is a product listed twice in one order rejected? Where is that enforced?

## Recommendation logic
- [ ] Why are all six permutations of the dimensions tested? How would you explain why sorting the sides gives the same answer?
- [ ] Why must total weight use `unit weight × quantity`?
- [ ] What exactly does the algorithm *not* guarantee for multi-product orders, and what example shows it?
- [ ] How would you improve it to do real 3D packing?

## Testing
- [ ] Why is the service tested with `SimpleTestCase` while models/views use `TestCase`?
- [ ] Which boundary cases did you test (exact fit, exact weight) and why do they matter?
- [ ] What bug or wrong assumption did a failing test reveal, and how did you fix it?

## Process
- [ ] Which parts did you understand fully, and which parts do you still need to study before an interview?
- [ ] What would you do differently next time when working with an AI assistant?
